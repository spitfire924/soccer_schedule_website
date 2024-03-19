from flask import Flask, render_template, request, redirect, url_for
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Dummy user credentials (replace with actual authentication logic)
VALID_USERNAME = "admin"
VALID_PASSWORD = "password"

# XML file path
XML_FILE = 'events.xml'

class Event:
    def __init__(self, name, date, location):
        self.name = name
        self.date = date
        self.location = location
        self.participants = []

    def add_participant(self, participant):
        self.participants.append(participant)

    def remove_participant(self, participant):
        if participant in self.participants:
            self.participants.remove(participant)
        else:
            print(f"{participant} is not a participant of this event.")

    def list_participants(self):
        return self.participants

    def count_participants(self):
        return len(self.participants)

def read_events_from_xml():
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        events = []
        for event_elem in root.findall('event'):
            name = event_elem.find('name').text
            date = event_elem.find('date').text
            location = event_elem.find('location').text
            event = Event(name, date, location)
            participants = [participant.text for participant in event_elem.findall('participant')]
            event.participants = participants
            events.append(event)
        return events
    except FileNotFoundError:
        return []

def write_events_to_xml(events):
    root = ET.Element('events')
    for event in events:
        event_elem = ET.SubElement(root, 'event')
        ET.SubElement(event_elem, 'name').text = event.name
        ET.SubElement(event_elem, 'date').text = event.date
        ET.SubElement(event_elem, 'location').text = event.location
        for participant in event.participants:
            ET.SubElement(event_elem, 'participant').text = participant
    tree = ET.ElementTree(root)
    tree.write(XML_FILE)

# Load events from XML file
events = read_events_from_xml()

@app.route('/')
def index():
    return render_template('index.html', events=events)

@app.route('/add_event', methods=['POST'])
def add_event():
    name = request.form['name']
    date = request.form['date']
    location = request.form['location']
    event = Event(name, date, location)
    events.append(event)
    write_events_to_xml(events)
    return redirect(url_for('index'))

@app.route('/event/<int:event_id>')
def view_event(event_id):
    event = events[event_id]  # Fetch the event from the events list
    return render_template('event.html', event=event, event_id=event_id)

@app.route('/add_participant/<int:event_id>', methods=['POST'])
def add_participant(event_id):
    participant = request.form['participant']
    events[event_id].add_participant(participant)
    write_events_to_xml(events)
    return redirect(url_for('view_event', event_id=event_id))

@app.route('/remove_participant/<int:event_id>/<participant>', methods=['POST'])
def remove_participant(event_id, participant):
    events[event_id].remove_participant(participant)
    write_events_to_xml(events)
    return redirect(url_for('view_event', event_id=event_id))
    
@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    del events[event_id]
    write_events_to_xml(events)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
