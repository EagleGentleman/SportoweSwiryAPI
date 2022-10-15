from flask import jsonify, abort
from SportoweSwiryAPI_app import db
from SportoweSwiryAPI_app.models import Event, Participation, EventSchema
from SportoweSwiryAPI_app.utilities import get_schema_args, apply_order, apply_filter,get_pagination, token_required, validate_json_content_type, filter_user_events
from SportoweSwiryAPI_app.events import events_bp

@events_bp.route('/events', methods=['GET'])
@token_required
def get_my_events(user_id: str):

    query = Event.query
    schema_args = get_schema_args(Event)
    query = filter_user_events(Participation, Event, query, user_id)
    query = apply_order(Event, query)
    query = apply_filter(Event, query)
    items, pagination = get_pagination(query, 'events.get_my_events')
    events=EventSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': events,
        'number_of_records': len(events),
        'pagination': pagination
    })


@events_bp.route('/all_events', methods=['GET'])
@token_required
def get_all_events(user_id: str):

    query = Event.query
    schema_args = get_schema_args(Event)
    query = apply_order(Event, query)
    query = apply_filter(Event, query)
    items, pagination = get_pagination(query, 'events.get_all_events')
    events=EventSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': events,
        'number_of_records': len(events),
        'pagination': pagination
    })


@events_bp.route("/join_event/<int:event_id>")
@token_required
def join_event(user_id: str, event_id: int):

    event = Event.query.get_or_404(event_id, description=f'Event with id {event_id} not found')

    if event.status == "Zapisy otwarte":
        is_participating = Participation.query.filter(Participation.user_id == user_id).filter(Participation.event_id == event_id).first()
        if is_participating == None:
            participation = Participation(user_id = user_id, event_id = event_id)
            db.session.add(participation)
            db.session.commit()
        else:
            abort(409, description=f'You are already signed up for this event ({event.name}).')
    else:
        abort(403, description=f'Joining for this event ({event.name}) is currently unavailable.')

    return jsonify({
        'success': True,
        'data': f'Congratulations. You signed up for event: {event.name}'
    })


@events_bp.route("/leave_event/<int:event_id>")
@token_required
def leave_event(user_id: str, event_id: int):

    event = Event.query.get_or_404(event_id, description=f'Event with id {event_id} not found')

    is_participating = Participation.query.filter(Participation.user_id == user_id).filter(Participation.event_id == event_id).first()
    if is_participating != None and event.status == "Zapisy otwarte":
        participation = Participation.query.filter(Participation.event_id==event_id).filter(Participation.user_id == user_id).first()
        db.session.delete(participation)
        db.session.commit()

    elif is_participating != None and event.status != "Zapisy otwarte":
        abort(403, description=f'It is no longer possible to leave an event ({event.name}) at this time.')
    elif is_participating == None:
        abort(409, description=f'You are not participating in this event ({event.name}).')

    return jsonify({
        'success': True,
        'data': f'You have been signed out of the event ({event.name})'
    })