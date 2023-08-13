from flask import Flask, render_template_string, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import os
from babel.numbers import format_currency
app = Flask(__name__)
# Use environment variable for secret key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'boobookitty')


class ComputeForm(FlaskForm):
    customer_name = StringField('Customer Name', validators=[
                                DataRequired(message='Please enter a customer name')])
    hourly_spend = FloatField(
        'Hourly Spend on Eligible Compute (in $)',
        validators=[NumberRange(
            0, 10000, message='Please enter a number between 0 and 10000')]
    )
    three_year_flex = FloatField('3 Year FlexCUD Commitment ($/hr)',
                                 validators=[
                                     NumberRange(0, 10000,
                                                 message='Please enter a number between 0 and 10000')
                                 ])
    one_year_flex = FloatField('1 Year FlexCUD Commitment ($/hr)', validators=[
                               NumberRange(0, 10000, message='Please enter a number between 0 and 10000')])

    sud_percentage = FloatField(
        'Percent of SUD (or ODVM) discount on OD Spend', validators=[NumberRange(0, 100, message='Please enter a number between 0 and 50')])

    submit = SubmitField('Push it. Push it real good.')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ComputeForm()
    cost_3_year_flex = None
    cost_1_year_flex = None
    cost_on_demand = None

    if form.validate_on_submit():
        # Perform calculations based on form input
        suds = form.sud_percentage.data/100
        commitment_1_year_flex = form.one_year_flex.data
        commitment_3_year_flex = form.three_year_flex.data

        cost_1_year_flex = (commitment_1_year_flex * (1-.28))

        cost_3_year_flex = (
            (commitment_3_year_flex) * (1-.46)
        )

        cost_on_demand = (
            (form.hourly_spend.data - form.three_year_flex.data -
             form.one_year_flex.data) * (1-suds)
        )

        total_cost = cost_1_year_flex + cost_3_year_flex + cost_on_demand

        overall_discount = (
            (form.hourly_spend.data - total_cost)/form.hourly_spend.data)

        discount = (form.hourly_spend.data - total_cost)/form.hourly_spend.data

        avail_hourly_od = (form.hourly_spend.data -
                           form.three_year_flex.data - form.one_year_flex.data)

        monthly_on_demand_cost = form.hourly_spend.data * 730

        monthly_discount_cost = total_cost * 730

        hourly_cost = form.hourly_spend.data

        suds_discount = (avail_hourly_od * suds * -1)

        final_hourly_od = avail_hourly_od + suds_discount

       # Provide feedback to the user
        flash(f"""
        <div>
        <table>
        <thead>
            <tr>
                <th class="name" colspan="2" style="font-size: 2em; text-align: center">{form.customer_name.data}</th>
            </tr>
        </thead>
        </div>
    <tr>
    <td class="label">Monthly On-Demand<br>Discount-Eligible Spend ($/mo)</td>
    <td class="data">{format_currency(monthly_on_demand_cost,currency='USD')}
    </td></tr>
    
    <tr>
        <td class="label">Hourly Spend ($/hr)</td>
        <td class="data">{format_currency(hourly_cost,currency='USD')}</td>
    </tr>
    
    <tr>
        <td class="header" colspan="2">Commitments</td>
    </tr>
    <tr>
        <td class="label">3 Year FlexCUD Commitment ($/hr)</td>
        <td class="data">{format_currency(commitment_3_year_flex, currency='USD')}</td>
    </tr>
    
    <tr>
    <td class="label">1 Year FlexCUD Commitment ($/hr)</td>
    <td class="data">{format_currency(commitment_1_year_flex,currency='USD')}
    </td></tr>
     <tr>
        <td class="header" colspan="2">Discounted Costs</td>
    </tr>
      
    <tr>
    <td class="label">1 Year FlexCUD Cost ($/hr)</td>
    <td class="data">{format_currency(cost_1_year_flex,currency='USD')}</td>
    </tr>
    <tr>
    <td class="label">3 Year FlexCUD Cost ($/hr)</td>
    <td class="data">{format_currency(cost_3_year_flex,currency='USD')}</td>
    </tr>
      <tr>
        <td class="header" colspan="2">On-Demand Discounting (SUDS, etc)</td>
    </tr>
    <tr>
    <td class="label">Remaining ODVM Costs ($/hr)</td>
    <td class="data">{format_currency(avail_hourly_od,currency='USD')}</td>
    </tr>
    <tr>
    <td class="label">SUDs (or ODVM) Discount</td>
    <td class="data">{format_currency(suds_discount,currency='USD')}</td>
    </tr>
    <tr>
    <td class="label">Final On-Demand Hourly Cost ($/hr)</td>
    <td class="data">{format_currency(final_hourly_od,currency='USD')}</td>
    </tr>
    <tr>
        <td class="header" colspan="2">Math</td>
    </tr>
    <tr>
    <td class="label">On-Demand Hourly Cost ($/hr)</td>
    <td class="data">{format_currency(final_hourly_od,currency='USD')}</td>
    </tr>
    <tr>
    <td class="label">+ 1 Yr FlexCUD Hourly Cost ($/hr)</td>
    <td class="data">{format_currency(cost_1_year_flex,currency='USD')}</td>
    </tr>
    <tr>
    <td class="label">+ 3 Yr FlexCUD Hourly Cost ($/hr)</td>
    <td class="data">{format_currency(cost_3_year_flex,currency='USD')}</td>
    </tr>  
    <tr>
    <td class="label">= Total Hourly Cost ($/hr)</td>
    <td class="data">{format_currency(total_cost,currency='USD')}</td>
    <tr>
    <td class="label">Total Monthly Cost ($/mo)</td>
    <td class="data">{format_currency(total_cost*730,currency='USD')}</td></tr>
    </tr></td>
    <tr>
    <td class="label">Discount (%)</td>
    <td class="data" >{discount*100:.2f}%</td></tr>
</table>
    """, "success")

        return redirect(url_for('index'))

    # Return the rendered form
    return render_template_string(TEMPLATE_STRING, form=form, title="FlexCUD Calculator Extravaganza")


TEMPLATE_STRING = '''
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{{title}}</title>
        <style>
            td {
                padding: 10px;
                font-size: 1.2em;
                margin: 10px;
                font-family: Arial, sans-serif;
            }
            td.label {
                text-align: left;
                }
            
            td.data {
                text-align: right;
                }
                
            td.header {
                font-size: 1.5em;
                font-weight: bold;
                text-align: center;
                }
                
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 10;
                padding: 10;
            }
            table {
                  width: 90%;
                border-collapse: collapse;
                    }
            table, th, td {
            border: 3px solid black;
            }
            td.label {
            padding: 8px;
            text-align: center;
            }

            h1 {
                background-color: #333;
                color: white;
                padding: 20px;
                text-align: center;
            }
            form {
                background-color: #fff;
                font-size: 1.4em;
                max-width: 500px;
                margin: 40px auto;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            
        
            p {
                margin-bottom: 10px;
            }
            label {
                display: ;
                margin-bottom: 1px;
            }
            input[type="text"], input[type="number"] {
                width: 90%;
                padding: 15px;
                border: 3px solid #119AFF;
                border-radius: 25px;
                ;
            }
            input[type="submit"] {
                background-color: #007BFF;
                color: #fff;;
                border: 5px solid #7BFF;
                border-radius: 15px;
                font-size: 1.3em;
                width: 100%;
                }
                
            input[type="submit"]:hover {
                background-color: #ADA;
                -webkit-transition: background-color 0.4s ease-in-out;
                                
            }
            ul {
                max-width: 700px;
                margin: 20px auto;
            }
            li {
                background-color: #FA1; /* for the success category, adjust if needed */
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 4px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .error {
                background-color: #FDD;
                }
}
        </style>
    </head>
    <body>
        <h1>{{title}}</h1>
        <form method="post">
            {{ form.hidden_tag() }}
            <p>{{ form.customer_name.label }}<br>{{ form.customer_name }}</p>
            <p>{{ form.hourly_spend.label }}<br>{{ form.hourly_spend }}</p>
            <p>{{ form.three_year_flex.label }}<br>{{ form.three_year_flex }}</p>
            <p>{{ form.one_year_flex.label }}<br>{{ form.one_year_flex }}</p>
            <p>{{ form.sud_percentage.label }}<br>{{ form.sud_percentage }}</p>
            <p>{{ form.submit() }}</p>
        </form>
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
