# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import requests
import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify, render_template

app = Flask(__name__)


def get_data_from_api(rent_date, open_id, certificate):
    url = "https://sdk.xyapi.game.qq.com/api/xiaoyue/helper/tool"

    params = {
        "rt": "json",
        "flag": 1,
        "source": "xy_sdk",
        "gameId": 1338,
        "openId": open_id,
        "certificate": certificate,
        "apiIndex": "1338_api_00001477",
        "size": 20000,
        "page": 0,
        "range": 7,
        "date": rent_date
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"请求失败，状态码：{response.status_code}")


def organize_data_by_name_and_change(data):
    organized_data = {}

    for item in data:
        # print(item)
        name = item["name"]
        change = item["change"]
        result = item["result"]

        if name not in organized_data:
            organized_data[name] = {"success_rates": {}}

        if change not in organized_data[name]:
            organized_data[name][change] = []

        organized_data[name][change].append(item)

        # 计算成功率

        current_level = int(change.split("→")[0])
        next_level = int(change.split("→")[1])

        if current_level not in organized_data[name]["success_rates"]:
            organized_data[name]["success_rates"][current_level] = {"success_count": 0, "total_count": 0}

        organized_data[name]["success_rates"][current_level]["total_count"] += 1
        if next_level > current_level:
            organized_data[name]["success_rates"][current_level]["success_count"] += 1


    return organized_data


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/get_data")
def get_data():
    open_id = request.args.get('openId')
    certificate = request.args.get('certificate')
    
    if not open_id or not certificate:
        return jsonify({"error": "Missing openId or certificate"}), 400

    current_date_str = datetime.now().strftime("%Y-%m-%d")
    data_list = []

    for _ in range(21):  # Fetch data for 21 weeks
        api_data = get_data_from_api(current_date_str, open_id, certificate)
        print(api_data)
        data_list.extend(api_data["result"]["list"])
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d") - timedelta(days=7)
        current_date_str = current_date.strftime("%Y-%m-%d")

    organized_data = organize_data_by_name_and_change(json.loads(json.dumps(data_list)))
    return jsonify(organized_data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")