import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

#random.seed(4888888888882)     # я закоментировал сид что бы программа каждый раз имитировала разные входные данные,
                               # иначе какой смысл в их генерации, ну и так интересней, но если вам надо глянуть статичные данные просто уберите хештег)
                               #кстати этот сид довольно таки интересный получился, там все гипотезы почти подтверждаются кроме последней.

sns.set_theme(style="whitegrid")  # красивенький фон к графику

# Часть 1. Генерация данных

# Выбираем месяцы, когда конкуренты будут вести себя агресивно и жестко демпинговать
aggressive_months = []
months_pool = list(range(1, 12))
random.shuffle(months_pool)

required_aggressive_months = random.choice([3, 4])

for month in months_pool:
    if len(aggressive_months) >= required_aggressive_months:
        break

    previous_month_is_busy = month - 1 in aggressive_months
    next_month_is_busy = month + 1 in aggressive_months        # я это написал чтобы не могло быть 2 месяца жестких убытков из за демпинга
                                                                # в моем магазине бы не дурачки работали, поэтому нельзя чтобы был упадок 2 месяца подряд
    if not previous_month_is_busy and not next_month_is_busy:
        aggressive_months.append(month)

aggressive_months.sort()

# Следующий месяц после агрессивного — это месяц восстановления
recovery_months = [month + 1 for month in aggressive_months if month < 12]

rows = []

for month in range(1, 13):
    # В конце года спрос обычно чуть выше
    q4_season = 1.2 if month in (10, 11, 12) else 1.0

    for category in ["GPU", "RAM"]:
        # Скидка в январе и августе — большая, а в остальные месяцы — маленькая (август - перед учебным годом скидка, а январь - нг)
        if month in (1, 8):
            discount_pct = round(random.uniform(0.10, 0.20), 4)
        else:
            discount_pct = round(random.uniform(0.01, 0.05), 4)

        # Маркетинг в двух специальных месяцах выше, чем обычно, что то типо эксперемента внутри компании
        if month in (3, 10):
            marketing_spend = round(random.uniform(320, 420), 2)
        else:
            marketing_spend = round(random.uniform(150, 240), 2)

        # Базовая цена конкурента зависит от категории и от месяца
        if category == "GPU":
            competitor_price = round(40000 + (month - 1) * (50000 / 11) + random.uniform(-2000, 2000), 2) # имитирую нестабильный рынок + инфляцию и округляю цену
            base_demand = 95
        else:
            competitor_price = round(6000 + (month - 1) * (12000 / 11) + random.uniform(-700, 700), 2)
            base_demand = 250

        is_aggressive = month in aggressive_months
        is_recovery = month in recovery_months

        # В агрессивные месяцы цена выше конкурента
        # В месяцы восстановления цена ниже конкурента, чтобы вернуть спрос
        if is_aggressive:
            price = round(competitor_price * random.uniform(1.08, 1.15), 2)
        elif is_recovery:
            price = round(competitor_price * random.uniform(0.92, 0.96), 2)
        else:
            price = round(competitor_price * random.uniform(0.93, 0.98), 2)

        # Сезонные скидки в январе и августе
        if month in (1, 8):
            price = round(price * (1 - discount_pct), 2)

        # Себестоимость зависит от цены и категории
        base_cost = round(price * random.uniform(0.40, 0.52) - (1800 if category == "GPU" else 400), 2)

        # Множители, которые влияют на спрос, расходы скидки и т.д.
        marketing_multiplier = 1.12 if marketing_spend > 300 else 1.04
        discount_boost = 1.08 if discount_pct > 0.15 else 1.0

        if price < competitor_price:
            price_factor = 1.7
        else:
            price_factor = 0.28

        if is_aggressive:
            price_factor *= 0.55
        elif is_recovery:
            price_factor *= 1.15

        # Итоговый спрос
        quantity_sold = int(
            max(
                1,
                base_demand
                * q4_season
                * price_factor
                * marketing_multiplier
                * discount_boost
                + random.uniform(-6, 12))) # макс и инт чтобы не уйти в минус и чтобы было целое число покупателей

        rows.append({"month": month,
                    "category": category,
                    "base_cost": base_cost,
                    "discount_pct": discount_pct,
                    "marketing_spend": marketing_spend,
                    "competitor_price": competitor_price,
                    "price": price,
                    "quantity_sold": quantity_sold,})


# Часть 2. Анализ данных

# Создаём DataFrame и сохраняем его в CSV
sales_df = pd.DataFrame(rows)
sales_df.to_csv("sales_business_data.csv", index=False)     # перевожу в сsv чтобы вторая часть программы была более автономной чтоли,
sales_df = pd.read_csv("sales_business_data.csv")                     # что бы могла читать сым файлы из вне, а не только наши вакумные данные


# Считаем выручку и чистую прибыль
sales_df["revenue"] = sales_df["price"] * sales_df["quantity_sold"]
sales_df["net_profit"] = sales_df["revenue"] - (sales_df["base_cost"] * sales_df["quantity_sold"]) - sales_df["marketing_spend"]

# Подготовим данные для графика
summary_df = sales_df[["month", "category", "net_profit"]].copy()

# Рисуем столбчатую диаграмму
plt.figure(figsize=(12, 7))
ax = sns.barplot(data=summary_df, x="month", y="net_profit", hue="category", palette="Set2")
ax.set_title("Чистая прибыль по месяцам и категориям", fontsize=16)
ax.set_xlabel("Месяц", fontsize=12)
ax.set_ylabel("Чистая прибыль, ₽", fontsize=12)
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax.legend(title="Категория")         # подписываем легенду гарфика и т.д.

# подписываем выручку за каждый месяц сверху графика и добавляем рублики ₽)
for container in ax.containers:
    ax.bar_label(container, fmt="{:,.0f} ₽", padding=3, fontsize=9)

plt.tight_layout()
#plt.savefig("sales_business_chart.png", dpi=300)  # я закоментил ибо зачем вам на компьютере сохранять фото графика? лишний мусор он и так виден, но если надо можно убрать хештег)
plt.show()

# Находим самые выгодные цены товара, при которых у нашей компании была максимальная чистая прибыль
gpu_best = sales_df[sales_df["category"] == "GPU"].sort_values("net_profit", ascending=False).iloc[0] # отсартировавываем датафрейм по выручке от больших значений к маленьким
ram_best = sales_df[sales_df["category"] == "RAM"].sort_values("net_profit", ascending=False).iloc[0] # и берем первую строку
#выводим данные
print(f"Самая выгодная цена у GPU: {gpu_best['price']:.2f}, покупателей: {int(gpu_best['quantity_sold'])}, чистая прибыль: {gpu_best['net_profit']:.0f} рублей")
print(f"Самая выгодная цена у RAM: {ram_best['price']:.2f}, покупателей: {int(ram_best['quantity_sold'])}, чистая прибыль: {ram_best['net_profit']:.0f} рублей")


# Функция для красивого вывода гипотез, красным ложные будут светиться а зеленом истинные ну еще добавил тру или фолс
def print_hypothesis(index, description, condition):
    color = "\033[92m" if condition else "\033[91m"
    status = "True" if condition else "False"
    print(f"{color}{index}. {description}: {status}\033[0m")


# Гипотеза 1: цена ниже конкурента — выше спрос
low_price_mask = sales_df["price"] < sales_df["competitor_price"]
high_price_mask = sales_df["price"] >= sales_df["competitor_price"]
condition_1 = sales_df.loc[low_price_mask, "quantity_sold"].mean() > sales_df.loc[high_price_mask, "quantity_sold"].mean() # накладваем маски, ищем среднее значение строк когда цена ниже конкурента
print_hypothesis(1, "Снижение цены на товар ниже средней цены конкурентов увеличивает спрос", condition_1)  # и выше, потом сравниваем для подтверждения или опровержениягипотезы

# Гипотеза 2: маржинальность GPU выше, чем у RAM
gpu_margin = sales_df.loc[sales_df["category"] == "GPU", "net_profit"].sum() / sales_df.loc[sales_df["category"] == "GPU", "revenue"].sum()
ram_margin = sales_df.loc[sales_df["category"] == "RAM", "net_profit"].sum() / sales_df.loc[sales_df["category"] == "RAM", "revenue"].sum()
condition_2 = gpu_margin > ram_margin
print_hypothesis(2, "Средняя маржинальность категории GPU выше, чем у RAM", condition_2)

# Гипотеза 3: маркетинг помогает GPU сильнее, чем RAM
marketing_high = sales_df[sales_df["marketing_spend"] > 300]
marketing_low = sales_df[sales_df["marketing_spend"] <= 300]

gpu_high_mean = marketing_high.loc[marketing_high["category"] == "GPU", "quantity_sold"].mean()
gpu_low_mean = marketing_low.loc[marketing_low["category"] == "GPU", "quantity_sold"].mean()
ram_high_mean = marketing_high.loc[marketing_high["category"] == "RAM", "quantity_sold"].mean()
ram_low_mean = marketing_low.loc[marketing_low["category"] == "RAM", "quantity_sold"].mean()

gpu_uplift = gpu_high_mean - gpu_low_mean
ram_uplift = ram_high_mean - ram_low_mean
condition_3 = gpu_uplift > ram_uplift
print_hypothesis(3, "Увеличение маркетингового бюджета производит положительный эффект на продажи GPU сильнее, чем на RAM", condition_3)

# Гипотеза 4: продажи в Q4 выше среднемесячных
monthly_sales = sales_df.groupby("month")["quantity_sold"].sum()
avg_monthly_sales = monthly_sales.mean()
q4_sales = monthly_sales.loc[[10, 11, 12]].mean()
condition_4 = q4_sales > avg_monthly_sales * 1.1
print_hypothesis(4, "Продажи в четвертом квартале выше среднемесячных продаж на 10%", condition_4)

# Гипотеза 5: большие скидки дают больше прибыли
high_discount = sales_df[sales_df["discount_pct"] > 0.15]
low_discount = sales_df[sales_df["discount_pct"] <= 0.15]
condition_5 = high_discount["net_profit"].mean() > low_discount["net_profit"].mean() # лень расписывать каждую гипотезу, тут и так понятно везде, ну типа берем булевную маску
print_hypothesis(5, "Скидки более 15% увеличивают чистую прибыль", condition_5) # накладываем и получаем два датафрейма сравниваем их средние показатели чистой прибыли и понимаем верная или ложная гипотеза

print(sales_df.head(4))
