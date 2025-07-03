# PricePeek

A lightweight tool to retrieve the current **average price** of a product using its name. Supports both **Python** and **Shell script** interfaces. Powered by [PriceAPI](https://www.priceapi.com/).

---

## ✨ Features

- Get real-time average market price of a product
- Simple and fast — input product name, get price
- Python and Shell script versions included
- Powered by the PriceAPI service

---

## 🔑 Setup

### 1. Get your API token

Register and get your token from [https://www.priceapi.com/](https://www.priceapi.com/).

### 2. Insert your API token
https://github.com/micelvrice/PricePeek/blob/bdc046a1d8089a563f952497bb9b75b0f7ff4610/get_average_price.py#L162
https://github.com/micelvrice/PricePeek/blob/bdc046a1d8089a563f952497bb9b75b0f7ff4610/get_average_price.sh#L11
---

### 2. Python Version

#### 🔧 Install dependencies

```bash
pip install requests

python get_average_price.py "iPhone 15"

### 3. Shell Version
bash get_average_price.sh "iPhone 15"
