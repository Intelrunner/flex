from flask import Flask, render_template_string, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import os

app = Flask(__name__)
# Use environment variable for secret key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'boobookitty')


class ComputeForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[DataRequired()])
    hourly_spend = FloatField(
        'Hourly Spend on Eligible Compute', validators=[DataRequired()])
    three_year_flex = FloatField('Percentage of 3 Year Flex', validators=[
                                 DataRequired(), NumberRange(0, 100)])
    one_year_flex = FloatField(
        'Percentage of 1 Year Flex', validators=[NumberRange(0, 100)])
    sud_percentage = FloatField(
        'Percentage of average SUD discount on OD Spend', validators=[NumberRange(0, 30)])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ComputeForm()
    on_demand_percentage = None
    cost_3_year_flex = None
    cost_1_year_flex = None
    cost_on_demand = None

    if form.validate_on_submit():
        # Perform calculations based on form input
        suds = form.sud_percentage.data/100
        on_demand_percentage = 100 - \
            (form.three_year_flex.data) - (form.one_year_flex.data)
        cost_1_year_flex = (form.hourly_spend.data *
                            form.one_year_flex.data/100 * (1-.28) * 730)
        cost_3_year_flex = (
            (form.hourly_spend.data * form.three_year_flex.data/100) * (1-.46)) * 730
        cost_on_demand = (form.hourly_spend.data *
                          on_demand_percentage/100 * (1-suds) * 730)
        total_cost = cost_1_year_flex + cost_3_year_flex + cost_on_demand
        overall_discount = ((form.hourly_spend.data * 730) -
                            total_cost) / (form.hourly_spend.data * 730)
       # Provide feedback to the user
        flash(f"""
        <table>
        <tr><td><strong>Customer Name:</strong></td><td>{form.customer_name.data}</td></tr>
        <tr><td><strong>Hourly Spend:</strong></td><td>${form.hourly_spend.data:.2f}</td></tr>
    <tr><td><strong>Monthly Spend:</strong></td><td>${form.hourly_spend.data * 730:.2f}</td></tr>
    <tr><td><strong>3 Year Flex Cost:</strong></td><td>{form.three_year_flex.data}% | ${cost_3_year_flex:.2f}</td></tr>
    <tr><td><strong>1 Year Flex Cost:</strong></td><td>{form.one_year_flex.data}% | ${cost_1_year_flex:.2f}</td></tr>
    <tr><td><strong>On Demand Cost:</strong></td><td>{on_demand_percentage:.2f}% | ${cost_on_demand:.2f}</td></tr>
    <tr><td><strong>Total:</strong></td><td>${total_cost:.2f}</td></tr>
    <tr><td><strong>Discount:</strong></td><td>{overall_discount*100:.2f}%</td></tr>
</table>
""", "success")

        return redirect(url_for('index'))

    # Return the rendered form
    return render_template_string(TEMPLATE_STRING, form=form, on_demand_percentage=on_demand_percentage)


TEMPLATE_STRING = '''
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Compute Form</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }
            table {
                  width: 100%;
                border-collapse: collapse;
                    }
            table, th, td {
            border: 1px solid #ddd;
            }
            td {
            padding: 8px;
            text-align: left;
            }

            h1 {
                background-color: #333;
                color: white;
                padding: 20px;
                text-align: center;
            }
            form {
                background-color: #fff;
                max-width: 500px;
                margin: 40px auto;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            p {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 10px;
            }
            input[type="text"], input[type="number"], input[type="submit"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            input[type="submit"] {
                background-color: #007BFF;
                color: #fff;
                cursor: pointer;
                border: none;
            }
            input[type="submit"]:hover {
                background-color: #0056b3;
            }
            ul {
                max-width: 500px;
                margin: 20px auto;
            }
            li {
                background-color: #dff0d8; /* for the success category, adjust if needed */
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 4px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <h1>Compute Form</h1>
        <form method="post">
            {{ form.hidden_tag() }}
            <p>{{ form.customer_name.label }}<br>{{ form.customer_name }}</p>
            <p>{{ form.hourly_spend.label }}<br>{{ form.hourly_spend }}</p>
            <p>{{ form.three_year_flex.label }}<br>{{ form.three_year_flex }}</p>
            <p>{{ form.one_year_flex.label }}<br>{{ form.one_year_flex }}</p>
            <p>{{ form.sud_percentage.label }}<br>{{ form.sud_percentage }}</p>
            <p>{{ form.submit() }}</p>
        </form>
        {% if on_demand_percentage is not none %}
            <p><strong>On Demand %:</strong> {{ on_demand_percentage }} %</p>
        {% endif %}
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        <ul>
            {% for category, message in messages %}
            <li{% if category %} class="{{ category }}"{% endif %}>{{ message|safe }}</li>

            {% endfor %}
        </ul>
        {% endif %}
        {% endwith %}
    </body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
