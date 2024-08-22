# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import requests
import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string, request, jsonify

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
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>成功率统计</title>
            <style>
                body {
                    margin: 0;
                    padding: 0;
                }
                .header {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    background-color: #fff;
                    z-index: 1000;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .tag-container {
                    padding: 15px;
                    border-bottom: 1px solid #e0e0e0;
                }
                .tag-list {
                    list-style-type: none;
                    padding: 0;
                    margin: 0;
                }
                .tag-list li {
                    display: inline-block;
                    margin-right: 10px;
                    margin-bottom: 10px;
                    margin-top: 10px;
                }
                .tag-list li a {
                    text-decoration: none;
                    padding: 5px 10px;
                    background-color: #f0f0f0;
                    border-radius: 3px;
                    color: #333;
                    cursor: pointer;
                }
                .tag-list li a.selected {
                    background-color: #007bff;
                    color: white;
                }
                .merge-button {
                    margin: 10px 15px;
                    padding: 5px 10px;
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }
                .content-area {
                    padding: 20px;
                }
                .input-container {
                    padding: 15px;
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #e0e0e0;
                }
                #linkInput {
                    width: 70%;
                    padding: 5px;
                    margin-right: 10px;
                }
                #submitLink {
                    padding: 5px 10px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="input-container">
                    <input type="text" id="linkInput" placeholder="输入链接">
                    <button id="submitLink">提交</button>
                </div>
                <h1 style="margin: 0; padding: 15px;">成功率统计</h1>
                <button id="mergeButton" class="merge-button">合并</button>
                <div class="tag-container">
                    <ul id="tagList" class="tag-list"></ul>
                </div>
            </div>
            <div id="contentArea" class="content-area"></div>

            <script>
                const mergeButton = document.getElementById('mergeButton');
                const tagList = document.getElementById('tagList');
                const contentArea = document.getElementById('contentArea');
                const header = document.querySelector('.header');
                let mergeMode = false;

                function updateContentAreaMargin() {
                    const headerHeight = header.offsetHeight;
                    contentArea.style.marginTop = `${headerHeight}px`;
                }

                // Call this function initially and whenever the window is resized
                updateContentAreaMargin();
                window.addEventListener('resize', updateContentAreaMargin);

                mergeButton.addEventListener('click', () => {
                    mergeMode = !mergeMode;
                    if (mergeMode) {
                        mergeButton.textContent = '确认合并';
                        tagList.classList.add('merge-mode');
                    } else {
                        mergeSelectedTags();
                        mergeButton.textContent = '合并';
                        tagList.classList.remove('merge-mode');
                    }
                });

                tagList.addEventListener('click', (e) => {
                    if (e.target.tagName === 'A') {
                        if (mergeMode) {
                            e.target.classList.toggle('selected');
                        } else {
                            const targetId = e.target.dataset.name;
                            const targetElement = document.getElementById(targetId);
                            if (targetElement) {
                                const headerHeight = header.offsetHeight;
                                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - headerHeight;
                                window.scrollTo({top: targetPosition, behavior: 'smooth'});
                            }
                        }
                    }
                });

                function mergeSelectedTags() {
                    const selectedTags = document.querySelectorAll('.tag-list a.selected');
                    if (selectedTags.length < 2) return;

                    const newName = Array.from(selectedTags).map(tag => tag.dataset.name).join('+');
                    const newContent = document.createElement('div');
                    newContent.className = 'content-section';
                    newContent.dataset.name = newName;

                    const newTitle = document.createElement('h2');
                    newTitle.id = newName;
                    newTitle.textContent = newName;
                    newContent.appendChild(newTitle);

                    const successRates = {};
                    const allItems = [];

                    selectedTags.forEach(tag => {
                        const name = tag.dataset.name;
                        const content = document.querySelector(`.content-section[data-name="${name}"]`);
                        
                        // Merge success rates
                        const rateTable = content.querySelector('table');
                        rateTable.querySelectorAll('tr:not(:first-child)').forEach(row => {
                            const level = row.cells[0].textContent.split('→')[0];
                            const rate = parseFloat(row.cells[1].textContent) / 100;
                            if (!successRates[level]) {
                                successRates[level] = { success: 0, total: 0 };
                            }
                            successRates[level].success += rate;
                            successRates[level].total += 1;
                        });

                        // Collect all items
                        const itemTable = content.querySelectorAll('table')[1];
                        itemTable.querySelectorAll('tr:not(:first-child)').forEach(row => {
                            allItems.push({
                                level: row.cells[0].textContent,
                                time: row.cells[1].textContent,
                                result: row.cells[2].textContent
                            });
                        });

                        // Remove old content
                        content.remove();
                        tag.parentElement.remove();
                    });

                    // Create new success rate table
                    const newRateTable = document.createElement('table');
                    newRateTable.border = '1';
                    newRateTable.innerHTML = `
                        <tr>
                            <th>强化等级</th>
                            <th>成功率</th>
                        </tr>
                    `;
                    const sortedLevels = Object.keys(successRates).sort((a, b) => parseInt(b) - parseInt(a));
                    for (const level of sortedLevels) {
                        const data = successRates[level];
                        const row = newRateTable.insertRow();
                        row.insertCell().textContent = `${level}→${parseInt(level) + 1}`;
                        row.insertCell().textContent = `${(data.success / data.total * 100).toFixed(2)}%`;
                    }
                    newContent.appendChild(newRateTable);

                    // Create new items table
                    const newItemTable = document.createElement('table');
                    newItemTable.border = '1';
                    newItemTable.innerHTML = `
                        <tr>
                            <th>目标强化等级</th>
                            <th>时间</th>
                            <th>结果</th>
                        </tr>
                    `;
                    allItems.forEach(item => {
                        const row = newItemTable.insertRow();
                        row.insertCell().textContent = item.level;
                        row.insertCell().textContent = item.time;
                        row.insertCell().textContent = item.result;
                    });
                    newContent.appendChild(newItemTable);

                    // Insert new content at the beginning of contentArea
                    contentArea.insertBefore(newContent, contentArea.firstChild);

                    // Create new tag
                    const newTag = document.createElement('li');
                    newTag.innerHTML = `<a data-name="${newName}">${newName}</a>`;
                    
                    // Insert new tag at the beginning of the tag list
                    tagList.insertBefore(newTag, tagList.firstChild);

                    // Remove old tags and content
                    selectedTags.forEach(tag => {
                        const name = tag.dataset.name;
                        const content = document.querySelector(`.content-section[data-name="${name}"]`);
                        if (content) content.remove();
                        tag.parentElement.remove();
                    });

                    // Reset selection state
                    document.querySelectorAll('.tag-list a.selected').forEach(tag => {
                        tag.classList.remove('selected');
                    });

                    // After merging, update the content area margin
                    updateContentAreaMargin();
                }

                document.getElementById('submitLink').addEventListener('click', function() {
                    const link = document.getElementById('linkInput').value;
                    const url = new URL(link);
                    const openId = url.searchParams.get('openId');
                    const certificate = url.searchParams.get('certificate');

                    if (openId && certificate) {
                        fetch(`/get_data?openId=${openId}&certificate=${certificate}`)
                            .then(response => response.json())
                            .then(data => {
                                // Update the page with the new data
                                updatePage(data);
                            })
                            .catch(error => {
                                console.error('Error:', error);
                                alert('获取数据失败，请检查链接是否正确。');
                            });
                    } else {
                        alert('链接中未找到 openId 或 certificate 参数。');
                    }
                });

                function updatePage(data) {
                    // Clear existing content
                    tagList.innerHTML = '';
                    contentArea.innerHTML = '';

                    // Update tags and content
                    for (const [name, itemData] of Object.entries(data)) {
                        const tagLi = document.createElement('li');
                        tagLi.innerHTML = `<a data-name="${name}">${name}</a>`;
                        tagList.appendChild(tagLi);

                        const contentSection = document.createElement('div');
                        contentSection.className = 'content-section';
                        contentSection.dataset.name = name;
                        contentSection.innerHTML = `
                            <h2 id="${name}">${name}</h2>
                            <p>成功率统计:</p>
                            <table border="1">
                                <tr>
                                    <th>强化等级</th>
                                    <th>成功率</th>
                                </tr>
                                ${Object.entries(itemData.success_rates).map(([level, stats]) => `
                                    <tr>
                                        <td>${level}→${parseInt(level) + 1}</td>
                                        <td>${(stats.success_count / stats.total_count * 100).toFixed(2)}%</td>
                                    </tr>
                                `).join('')}
                            </table>
                            <br>
                            <table border="1">
                                <tr>
                                    <th>目标强化等级</th>
                                    <th>时间</th>
                                    <th>结果</th>
                                </tr>
                                ${Object.entries(itemData).filter(([key]) => key !== 'success_rates').flatMap(([change, items]) => 
                                    items.map(item => `
                                        <tr>
                                            <td>${change.split("→")[1]}</td>
                                            <td>${item.time}</td>
                                            <td>${item.result}</td>
                                        </tr>
                                    `)
                                ).join('')}
                            </table>
                        `;
                        contentArea.appendChild(contentSection);
                    }

                    updateContentAreaMargin();
                }
            </script>
        </body>
        </html>
    ''')


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
        data_list.extend(api_data["result"]["list"])
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d") - timedelta(days=7)
        current_date_str = current_date.strftime("%Y-%m-%d")

    organized_data = organize_data_by_name_and_change(json.loads(json.dumps(data_list)))
    return jsonify(organized_data)


if __name__ == "__main__":
    app.run(debug=True)