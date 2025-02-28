from flask import Flask, request
import numpy as np
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={"/speechbox": {"origins": ["http://localhost:5150", "https://localhost:7054"]}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/speechbox", methods=['POST'])
def speechbox():
    group_by_speaker = True

    json_data = request.get_json()

    segments = json_data["diarization"]

    # diarizer output may contain consecutive segments from the same speaker (e.g. {(0 -> 1, speaker_1), (1 -> 1.5, speaker_1), ...})
    # we combine these segments to give overall timestamps for each speaker's turn (e.g. {(0 -> 1.5, speaker_1), ...})
    new_segments = []
    prev_segment = cur_segment = segments[0]

    for i in range(1, len(segments)):
        cur_segment = segments[i]

        # check if we have changed speaker ("label")
        if cur_segment["label"] != prev_segment["label"] and i < len(segments):
            # add the start/end times for the super-segment to the new list
            new_segments.append(
                {
                    "segment": {"start": prev_segment["segment"]["start"], "end": cur_segment["segment"]["start"]},
                    "speaker": prev_segment["label"],
                }
            )
            prev_segment = segments[i]

    # add the last segment(s) if there was no speaker change
    new_segments.append(
        {
            "segment": {"start": prev_segment["segment"]["start"], "end": cur_segment["segment"]["end"]},
            "speaker": prev_segment["label"],
        }
    )

    transcript = json_data["asr"]

    # get the end timestamps for each chunk from the ASR output
    end_timestamps = np.array([chunk["timestamp"][-1] for chunk in transcript])
    segmented_preds = []

    # align the diarizer timestamps and the ASR timestamps
    for segment in new_segments:
        # get the diarizer end timestamp
        end_time = segment["segment"]["end"]
        # find the ASR end timestamp that is closest to the diarizer's end timestamp and cut the transcript to here
        try:
            upto_idx = np.argmin(np.abs(end_timestamps - end_time))
        except ValueError:
            continue

        if group_by_speaker:
            grouped_text = "".join([chunk["text"] for chunk in transcript[: upto_idx + 1]])
            if (grouped_text == "" or grouped_text == " "):
                continue

            segmented_preds.append(
                {
                    "speaker": segment["speaker"],
                    "text": grouped_text,
                    "timestamp": (transcript[0]["timestamp"][0], transcript[upto_idx]["timestamp"][1]),
                }
            )
        else:
            for i in range(upto_idx + 1):
                segmented_preds.append({"speaker": segment["speaker"], **transcript[i]})

        # crop the transcripts and timestamp lists according to the latest timestamp (for faster argmin)
        transcript = transcript[upto_idx + 1 :]
        end_timestamps = end_timestamps[upto_idx + 1 :]

    return segmented_preds


@app.route("/hello")
def hello_world():
    return "Hello, World!"