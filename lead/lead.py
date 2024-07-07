from flask import Blueprint, flash, jsonify, render_template, request, redirect, url_for, session
from sql.db import DB
from lead.forms import LeadForm
from flask_principal import Permission, RoleNeed
from roles.permissions import sales_or_admin_permission
from werkzeug.datastructures import MultiDict
from datetime import datetime, date
import openai
import json
import os
import time
from flask import jsonify
from collections import Counter

openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI()

leads = Blueprint('leads', __name__, url_prefix='/leads', template_folder='templates')

@leads.route("/add", methods=["GET", "POST"])
@sales_or_admin_permission.require(http_exception=403)
def add():
    form = LeadForm()
    if form.validate_on_submit():
        try:
            result = DB.insertOne("INSERT INTO SMART_Leads (customer_name, enterprise_name, lead_type, domain, todo_actions, next_follow_up, action_needed) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            form.customer_name.data, form.enterprise_name.data, form.lead_type.data, form.domain.data, form.todo_actions.data, form.next_follow_up.data.strftime('%Y-%m-%d'), form.action_needed.data)
            if result.status:
                flash(f"Created lead {form.customer_name.data}", "success")
        except Exception as e:
            flash(f"Error creating lead: {e}", "danger")
    return render_template("lead_form.html", form=form, type="Create")

@leads.route("/edit", methods=["GET", "POST"])
@sales_or_admin_permission.require(http_exception=403)
def edit():
    form = LeadForm()
    id = request.args.get("id")
    if id is None:
        flash("Missing id", "danger")
        return redirect(url_for("leads.list"))
    if form.validate_on_submit() and id:
        try:
            result = DB.insertOne("UPDATE SMART_Leads SET customer_name = %s, enterprise_name = %s, lead_type = %s, domain = %s, todo_actions = %s, next_follow_up = %s, action_needed = %s WHERE id = %s",
            form.customer_name.data, form.enterprise_name.data, form.lead_type.data, form.domain.data, form.todo_actions.data, form.next_follow_up.data.strftime('%Y-%m-%d'), form.action_needed.data, id)
            if result.status:
                flash(f"Updated lead {form.customer_name.data}", "success")
        except Exception as e:
            flash(f"Error updating lead: {e}", "danger")
    try:
        result = DB.selectOne("SELECT customer_name, enterprise_name, lead_type, domain, todo_actions, next_follow_up, action_needed FROM SMART_Leads WHERE id = %s", id)
        if result.status and result.row:
            row = result.row
            if isinstance(row['next_follow_up'], (datetime, date)):
                row['next_follow_up'] = row['next_follow_up'].strftime('%Y-%m-%d')
            form = LeadForm(MultiDict(row))
    except Exception as e:
        flash(f"Error fetching lead: {e}", "danger")
    return render_template("lead_form.html", form=form, type="Edit")

@leads.route("/list", methods=["GET"])
@sales_or_admin_permission.require(http_exception=403)
def list():
    rows = []
    try:
        result = DB.selectAll("SELECT id, customer_name, enterprise_name, lead_type, domain, todo_actions, next_follow_up, action_needed FROM SMART_Leads LIMIT 100")
        if result.status and result.rows:
            rows = result.rows
            # TODO Dates to String 
            for row in rows:
                if isinstance(row['next_follow_up'], (datetime, date)):
                    row['next_follow_up'] = row['next_follow_up'].strftime('%Y-%m-%d')
    except Exception as e:
        flash(f"Error fetching leads: {e}", "danger")
    return render_template("leads_list.html", rows=rows)

@leads.route("/delete", methods=["GET"])
@sales_or_admin_permission.require(http_exception=403)
def delete():
    id = request.args.get("id")
    if id:
        try:
            result = DB.delete("DELETE FROM SMART_Leads WHERE id = %s", id)
            if result.status:
                flash("Deleted lead", "success")
        except Exception as e:
            flash(f"Error deleting lead: {e}", "danger")
    else:
        flash("No id present", "warning")
    return redirect(url_for("leads.list"))

@leads.route("/parse_voice_input", methods=["POST"])
def parse_voice_input():
    data = request.get_json()
    transcript = data.get('transcript', '')
    
    if not transcript:
        return jsonify({'status': 'error', 'message': 'No transcript provided'})

    # TODO Conversation history in session
    if 'conversation' not in session:
        session['conversation'] = []

    session['conversation'].append({"role": "user", "content": transcript})
    session.modified = True

    # TODO Limit the API calls to 1/min
    current_time = time.time()
    if 'last_api_call' not in session or current_time - session['last_api_call'] > 60:
        try:
            lead_info = extract_lead_info(session['conversation'])
            session['conversation'].append({"role": "assistant", "content": json.dumps(lead_info)})
            session['last_api_call'] = current_time
            return jsonify({'status': 'success', 'lead_info': lead_info})
        except openai.APIError as e:
            return jsonify({'status': 'error', 'message': f'OpenAI API returned an API Error: {e}'})
        except openai.APIConnectionError as e:
            return jsonify({'status': 'error', 'message': f'Failed to connect to OpenAI API: {e}'})
        except openai.RateLimitError as e:
            return jsonify({'status': 'error', 'message': f'OpenAI API request exceeded rate limit: {e}'})
        except Exception as e:
            print(f"Error processing transcript: {e}")
            return jsonify({'status': 'error', 'message': str(e)})
    else:
        return jsonify({'status': 'success', 'message': 'Transcript received. Waiting for next API call.'})

def construct_prompt(conversation):
    prompt = """
    ####
    You are an assistant that extracts information from call transcripts of lead and TikTok's executive. Identify the customer in this conversation and these details which are expected are of the customer.
    ####
    Please extract the following details from the provided call transcript and return the output in JSON format only and in bracket description of these fields are give for your context:
    - customer_name (the person who wants to get help)
    - enterprise_name (customer's company name)
    - lead_type (can be a Key-Word)
    - domain (Identify the Domain for the company/customer)
    - todo_actions (What action are required from TikTok's Team)
    - next_follow_up (in YYYY-MM-DD format) (might be asked by executive or given by the customer - if only month then use 01 for the date)
    - action_needed (true or false) (Is any action needed from TikTok for the customer.)
    ####
    Ensure the output is a well-formed JSON object and contains only the extracted information.
    """
    return {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": prompt}] + conversation,
        "max_tokens": 150,
        "temperature": 0.7
    }

def extract_lead_info(conversation):
    response = client.chat.completions.create(**construct_prompt(conversation))
    lead_info_raw = response.choices[0].message.content.strip()
    return parse_output(lead_info_raw)

def parse_output(raw_output):
    try:
        lead_info = json.loads(raw_output)
        return lead_info
    except json.JSONDecodeError:
        cleaned_output = clean_output(raw_output)
        try:
            lead_info = json.loads(cleaned_output)
            return lead_info
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON output")

def clean_output(output):
    start_index = output.find('{')
    end_index = output.rfind('}') + 1
    if start_index != -1 and end_index != -1:
        return output[start_index:end_index]
    return output

def parse_lead_info(lead_info_raw):
    lead_info = {
        'customer_name': '',
        'enterprise_name': '',
        'lead_type': '',
        'domain': '',
        'todo_actions': '',
        'next_follow_up': '',
        'action_needed': False
    }
    
    for line in lead_info_raw.split('\n'):
        try:
            key, value = line.split(':')
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            if key in lead_info:
                if key == 'action_needed':
                    lead_info[key] = value.lower() == 'true'
                else:
                    lead_info[key] = value
        except ValueError:
            print(f"Skipping line: {line}")
            continue
    
    return lead_info

#TODO Analytics for landing page

@leads.route('/analytics', methods=['GET'])
def analytics():
    lead_types = Counter()
    lead_statuses = Counter()

    try:
        result = DB.selectAll("SELECT lead_type, action_needed FROM SMART_Leads")
        if result.status and result.rows:
            for row in result.rows:
                lead_types[row['lead_type']] += 1
                lead_statuses['Action Needed' if row['action_needed'] else 'No Action Needed'] += 1

        return jsonify({
            'lead_types': lead_types,
            'lead_statuses': lead_statuses
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
