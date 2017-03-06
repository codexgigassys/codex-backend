import pathmagic
from bottle import route, request, response
from Utils.Functions import jsonize, change_date_to_str
from PackageControl.PackageController import *


@route('/api/v1/last_uploaded', method='GET')
# Returns a json with the last n files
# added to the database.
def last_uploaded():
    number = request.query.get("n")
    if number is None:
        response.status = 400
        return jsonize({"error": 1, "error_message": "Parameter n is missing"})
    if number.isdigit() is False:
        response.status = 400
        return jsonize({"error": 2, "error_message": "Parameter n must be a number"})
    if int(number) == 0:
        return jsonize({"error": 3, "error_message": "Parameter n must be greater than zero."})

    pc = PackageController()
    lasts = pc.last_updated(int(number))
    for i in range(0, len(lasts)):  # Convert datetime objects
        lasts[i] = change_date_to_str(lasts[i])
    return jsonize(lasts)
