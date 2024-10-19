import requests


def checkSecurityExistence(security_id):
    url = f"https://iss.moex.com/iss/securities/{security_id}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        exist = data.get("boards", {}).get("data", [])
        return bool(exist)
    else:
        return False


def getSecurityPrice(security_id):
    try:
        assert checkSecurityExistence(security_id)
    except:
        return None
    url_stock = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{security_id}.json?iss.only=securities&securities.columns=PREVPRICE,CURRENCYID"
    #url_bond = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities/{security_id}.json?iss.only=securities&securities.columns=PREVPRICE,CURRENCYID"
    response = requests.get(url_stock)
    if response.status_code == 200:
        data = response.json()
        stock_price = data.get("securities", {}).get("data", [[]])[0][0]
        stock_currency = data.get("securities", {}).get("data", [[]])[0][1]
        if stock_currency not in ["SUR", "RUB"]:
            return None
        return stock_price
    return None


print(getSecurityPrice(""))