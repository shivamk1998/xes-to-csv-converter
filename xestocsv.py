# import pandas as pd
# from pm4py.objects.log.importer.xes import importer as xes_importer

# # Load the XES file
# log = xes_importer.apply("Road_Traffic_Fine_Management_Process.xes")

# # Convert to a DataFrame
# events = []
# for trace in log:
#     for event in trace:
#         events.append(event)

# df = pd.DataFrame(events)

# # Save to CSV
# df.to_csv("Road_Traffic_Fine_Management_Process.csv", index=False)


from flask import Flask, request, render_template, send_file
import pandas as pd
from pm4py.objects.log.importer.xes import importer as xes_importer
import io
import tempfile

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    if 'xes_file' not in request.files:
        return "No file part"

    file = request.files['xes_file']
    if file.filename == '':
        return "No selected file"

    try:
        # Use a temporary file to save the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xes') as temp_file:
            # Save the uploaded file to the temporary file
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        # Read the log from the temporary file
        log = xes_importer.apply(temp_file_path)

        events = []
        for trace in log:
            for event in trace:
                events.append(event)
        df = pd.DataFrame(events)

        # Create a CSV buffer
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Clean up the temporary file
        # You may want to keep it or remove it later
        # os.remove(temp_file_path)

        # Return the CSV file as a downloadable response
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='output.csv'
        )

    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)
