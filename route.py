# from flask import Flask, render_template, request,url_for,redirect
# from pymongo import MongoClient
# import gridfs 

# client = MongoClient("mongodb+srv://---------redacted---------:----------redacted-----------@cluster0.4crcv.mongodb.net/")
# db = client["CrisisReport"]
# collection = db["reports"]

# app=Flask(__name__)

# @app.route('/')
# def citizen():
    
#     return render_template('citizen.html')

# @app.route('/form',methods=['POST'])

# def form():
#     location = request.form.get('location')
#     description = request.form.get('description')
#     media = request.files.getlist('media')
#     # Save to MongoDB
#     report_data = {
#         "location": location,
#         "description": description,
#         "media": []
#     }
#     for file in media:
#         with open(file.filename, "rb") as f:
#             report_data["media"].append(f.read())
#     collection.insert_one(report_data)
    

#     return redirect(url_for('citizen'))

# if __name__=="__main__":
#     app.run(debug=True)


import os
from flask import Flask, render_template, request, url_for, redirect,render_template_string,jsonify
from pymongo import MongoClient
import gridfs
from datetime import datetime
import folium 
import folium.plugins
from opencage.geocoder import OpenCageGeocode
from dotenv import load_dotenv

# Add these imports at the top of route.py
from bson.objectid import ObjectId
from flask import send_file
import io

mongodb_uri=os.getenv("mongodb_uri")
client = MongoClient(mongodb_uri)
db = client["CrisisReport"]
collection = db["reports"]
fs = gridfs.GridFS(db)

app = Flask(__name__)






@app.route('/media/<file_id>')
def get_media(file_id):
    try:
        file_data = fs.get(ObjectId(file_id))
        return send_file(
            io.BytesIO(file_data.read()),
            mimetype=file_data.content_type
        )
    except Exception as e:
        return f"Error: {str(e)}", 404





@app.route('/')
def citizen():
    # Fetch all reports and sort by timestamp in descending order (-1)
    reports = collection.find().sort("timestamp", -1)
    
    # Format the reports for template
    formatted_reports = []
    for report in reports:
        report_data = {
            "crisis_type": report["crisis_type"],
            "location": report["location"],
            "description": report["description"],
            "upvotes": report.get("upvotes", 0),
            "comments": report.get("comments", 0),
            "shares": report.get("shares", 0),
            "timestamp": report["timestamp"],
            "media": []
        }
        # print(report_data.get('crisis_type'))
        
        # Get media files from GridFS
        for media_id in report.get("media_ids", []):
            try:
                file_data = fs.get(ObjectId(media_id))
                media_info = {
                    "id": str(media_id),
                    "content_type": file_data.content_type,
                    "filename": file_data.filename
                }
                report_data["media"].append(media_info)
            except Exception as e:
                print(f"Error fetching media {media_id}: {e}")
        
        formatted_reports.append(report_data)

    return render_template('citizen.html', reports=formatted_reports)

@app.route('/form', methods=['POST'])
def form():
    def get_location_name(lat, lng):
        OPENCAGE_KEY = "d22765be25474fb9a45d9f1a2b30853f"  # Replace with your API key
        geocoder = OpenCageGeocode(OPENCAGE_KEY)

        try:
            result = geocoder.reverse_geocode(lat, lng)
            if result and len(result):
                # Get the formatted address
                location_name = result[0]['formatted']
                return location_name
            return f"{lat}, {lng}"  # Return coordinates if no address found
        except Exception as e:
            print(f"Geocoding error: {e}")
    location = request.form.get('location')
    print(location)
    loc1=location
    try:
        lat,lng=map(str.strip,loc1.split(','))
        if lat=='' or lng=='':
            raise ValueError("got name insted lat lng")
        location=get_location_name(lat,lng)
        # location=geocoder.reverse_geocode(lat,lng)
    except ValueError:
        OPENCAGE_KEY = "d22765be25474fb9a45d9f1a2b30853f"
        geocoder = OpenCageGeocode(OPENCAGE_KEY)
        results = geocoder.geocode(location)
        
        if results:
            lat = results[0]["geometry"]["lat"]
            lng = results[0]["geometry"]["lng"]
        else:
            print("error finding location through name")


    description = request.form.get('description')
    media_files = request.files.getlist('media')
    crisis_type=request.form.get('crisis_type')
    # Create report data
    report_data = {
        "crisis_type": crisis_type,
        "location": location,
        "lat": lat,
        "lng": lng,
        "description": description,
        "upvotes": 0,
        "comments": 0,
        "shares": 0,
        "media_ids": [],  # Store GridFS file IDs
        "timestamp": datetime.now()
    }
    # print(report_data.get('crisis_type'))

    # Handle media files
    for file in media_files:
        if file and file.filename:
            # Save file to GridFS
            file_id = fs.put(
                file.read(),
                filename=file.filename+"_"+str(datetime.now().timestamp()),
                content_type=file.content_type
            )
            report_data["media_ids"].append(str(file_id))
    
    # Insert report into MongoDB
    collection.insert_one(report_data)
    
    return redirect(url_for('citizen'))


# @app.route("/map",methods=['GET'])
# def map_view():
    # foliumMap=folium.Map(location=[19.6905763,61.0283225], zoom_start=5, width=750, height=500)

    
    # # render the map on the webpage
    # foliumMap.get_root().render()
    # header=foliumMap.get_root().header.render()
    
    # map=foliumMap.get_root().html.render()
    # script=foliumMap.get_root().script.render()
    # # print(map,script,header)
    # # return render_template_string( '''
    # #         <html>
    # #         <head>
    # #             {{header|safe}}
    # #         </head>
    # #         <body>
    # #             {{map|safe}}

    # #         <script>
    # #                 {{script|safe}}
    # #         </script>
    # #         </body>
                                  
    # #         </html>''',header=header,map=map,script=script)
    # return render_template('citizen.html',header=header,map=map,script=script)
# @app.route("/map")
# def map_view():
#     # Create map centered at India
#     foliumMap = folium.Map(
#         location=[20.5937, 78.9629],
#         zoom_start=5,
#         tiles='OpenStreetMap'
#     )

#     # Fetch all reports from MongoDB
#     reports = collection.find()
#     print(reports)
#     # Add markers for each report
#     for report in reports:
#         # Try to extract coordinates from location string (assuming format: "lat, long")
#         try:
#             lat, lng = float(report.get('lat')), float(report.get('lng'))

#             # Create popup content
#             # popup_content = f"""
#             #     <div style='width:200px'>
#             #         <h4>{report['crisis_type']}</h4>
#             #         <p>{report['description']}</p>
#             #         <small>{report['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
#             #     </div>
#             # """
            
#             # Choose icon color based on crisis type
#             # icon_color = 'red' if '🚧 Hazard' in report['crisis_type'] else 'blue'
#             # Add pulsating effect CSS
#             heatwave_css = """
#             <style>
#             .pulse {
#               position: relative;
#               width: 20px;
#               height: 20px;
#               background: rgba(0, 123, 255, 0.5);  /* default blue */
#               border-radius: 50%;
#             }
#             .pulse::after {
#               content: "";
#               position: absolute;
#               width: 20px;
#               height: 20px;
#               border-radius: 50%;
#               background: inherit;
#               animation: pulse-animation 2s infinite;
#             }
#             @keyframes pulse-animation {
#               0% { transform: scale(1); opacity: 0.7; }
#               70% { transform: scale(3); opacity: 0; }
#               100% { transform: scale(1); opacity: 0; }
#             }
#             .pulse-red { background: rgba(255, 0, 0, 0.5); }
#             .pulse-blue { background: rgba(0, 123, 255, 0.5); }
#             .pulse-orange { background: rgba(255, 165, 0, 0.5); }
#             </style>
#             """
#             foliumMap.get_root().html.add_child(folium.Element(heatwave_css))
            
          
#             markers = []
    
            
#             # Add marker to map
#             if '🚧 Hazard' in report['crisis_type']:
#                 color_class = 'pulse-red'
#             elif '⚠️ Information' in report['crisis_type']:
#                 color_class = 'pulse-blue'
#             else :
#                 color_class = 'pulse-orange'
            
#             folium.Marker(
#                 location=[lat, lng],
#                 popup=f"type:{report['crisis_type']}, description:{report['description']}, timestamp:{report['timestamp'].strftime('%Y-%m-%d %H:%M')}",
#                 icon=folium.DivIcon(
#                 html=f'<div class="pulse {color_class}"></div>'
#             ),
#                 tooltip=report['crisis_type']
#             ).add_to(foliumMap)
#         except:
#             continue

    # Add search control
    # foliumMap.add_child(folium.plugins.Search(
    #     layer=foliumMap,
    #     search_label='location',
    #     position='topright'
    # ))

    # Add fullscreen control
    # foliumMap.add_child(folium.plugins.Fullscreen())

    # # Add layer control
    # folium.LayerControl().add_to(foliumMap)

    # # Get map components
    # foliumMap.get_root().render()
    # header = foliumMap.get_root().header.render()
    # map_html = foliumMap.get_root().html.render()
    # script = foliumMap.get_root().script.render()

    # return render_template('citizen.html', header=header, map=map_html, script=script)


# @app.route("/markers")
# def get_markers():
#     reports = collection.find()
#     markers = []
    
#     for report in reports:
#         try:
#             markers.append({
#                 'lat': float(report.get('lat')),
#                 'lng': float(report.get('lng')),
#                 'type': report.get('crisis_type'),
#                 'description': report.get('description'),
#                 'timestamp': report.get('timestamp').strftime('%Y-%m-%d %H:%M')
#             })
#         except:
#             continue
    
#     return jsonify(markers)


@app.route("/map")
def map_view():
    # Create map centered at India (Vadodara coordinates)
    foliumMap = folium.Map(
        location=[20.5937, 78.9629],
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Fetch all reports from MongoDB
    reports = collection.find()
    # print(reports)
    
    # CSS for pulsating effect
    heatwave_css = """
    <style>
    .pulse {
        position: relative;
        width: 20px;
        height: 20px;
        background: rgba(0, 123, 255, 0.5); /* default blue */
        border-radius: 50%;
    }
    .pulse::after {
        content: "";
        position: absolute;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: inherit;
        animation: pulse-animation 2s infinite;
    }
    @keyframes pulse-animation {
        0% { transform: scale(1); opacity: 0.7; }
        70% { transform: scale(3); opacity: 0; }
        100% { transform: scale(1); opacity: 0; }
    }
    .pulse-red { background: rgba(255, 0, 0, 0.5); }
    .pulse-blue { background: rgba(0, 123, 255, 0.5); }
    .pulse-orange { background: rgba(255, 165, 0, 0.5); }
    </style>
    """
    
    # Add CSS to map
    foliumMap.get_root().html.add_child(folium.Element(heatwave_css))
    
    # Add markers for each report
    for report in reports:
        try:
            # Extract coordinates from location string (assuming format: "lat, lng")
            lat, lng = float(report.get('lat')), float(report.get('lng'))
            
            # Choose icon color based on crisis type
            if '🚧 Hazard' in report['crisis_type']:
                color_class = 'pulse-red'
            elif '⚠️ Information' in report['crisis_type']:
                color_class = 'pulse-blue'
            else:
                color_class = 'pulse-orange'
            
            # Create popup content
            popup_content = f"""
            <div style='width:200px'>
                <h4>{report['location']}</h4>
                <h4>{report['crisis_type']}</h4>
                <p>{report['description']}</p>
                <small>{report['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """
            
            # Add marker to map
            folium.Marker(
                location=[lat, lng],
                popup=popup_content,
                icon=folium.DivIcon(
                    html=f'<div class="pulse {color_class}"></div>',
                    icon_size=(20, 20)
                ),
                tooltip=report['crisis_type']
            ).add_to(foliumMap)
            
        except (ValueError, KeyError, TypeError) as e:
            print(f"Error processing report: {e}")
            continue

    # Add fullscreen control
    
    foliumMap.add_child(folium.plugins.Fullscreen())

    # Add layer control
    # folium.LayerControl().add_to(foliumMap)
    foliumMap.save('templates/map.html',)

    return render_template('map.html')


@app.route('/admin')
def admin():
    return render_template('admin.html', pending_reports=collection.find({"status": "pending"}))




if __name__ == "__main__":
    app.run(debug=True)