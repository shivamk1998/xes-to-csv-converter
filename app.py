from flask import Flask, request, send_file, jsonify
from flask_cors import CORS 
import pandas as pd
from pm4py.objects.log.importer.xes import importer as xes_importer
import io
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    return "hello World"
    if 'xes_file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['xes_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xes') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        # Read the log from the temporary file
        log = xes_importer.apply(temp_file_path)
        
        # Extract events
        events = []
        for trace in log:
            for event in trace:
                events.append(event)
        df = pd.DataFrame(events)

        # Create a CSV buffer
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Return the CSV file as a downloadable response
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='output.csv'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
