import seaborn as sns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd


df = pd.read_csv("C:/Users/creek/Desktop/Ideathon/property_assessments_post.csv")
housing_supply = len(df.index)
print("Total housing units in Pittsburgh: " + str(housing_supply))
med_price = np.median(df['fairmarkettotal'])
PRICE_TO_RENT = 9.34
print("Median home price in Pittsburgh: " + str(med_price))
ELASTICITY_SUPPLY = 2.2 #from https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3520650
TARGET_HOMES = 17491
supplies = np.linspace(450000, 550000, 100)

def price_from_supply(supply):
    d_supply = supply - housing_supply
    r_change_supply = float(d_supply)/float(housing_supply)
    r_change_price = r_change_supply*(1/ELASTICITY_SUPPLY)
    d_price = r_change_price*med_price
    return d_price + med_price

prices = [price_from_supply(s) / PRICE_TO_RENT for s in supplies]
p = sns.lineplot(x=supplies, y=prices)
p.set(title="Pittsburgh Housing Supply Curve")
p.set_xlabel("Supply Quantity (Q)")
p.set_ylabel("Price (P)")

Q_V = 17491 #number of vacant homes

print("Q_1 = " + str(housing_supply))
print("Q_2 = " + str(housing_supply+Q_V))
print("P_1 = " + str(med_price / PRICE_TO_RENT))

AFFORDABILITY_THRESHOLD = 6001 * PRICE_TO_RENT #calculated from housing cost burden and price to rent ratio

unaffordable = df[df.fairmarkettotal > AFFORDABILITY_THRESHOLD]

expensive_affordable_home = unaffordable.fairmarkettotal.nsmallest(TARGET_HOMES).iloc[-1]
marginal_homes = unaffordable.nsmallest(TARGET_HOMES, 'fairmarkettotal')
neighborhoods = marginal_homes.neighborhood.value_counts()

needed_price_shift = AFFORDABILITY_THRESHOLD/expensive_affordable_home
print("We need a price decrease of " + str(needed_price_shift))

print("P_2 = " + str(needed_price_shift * (med_price/PRICE_TO_RENT)))

print("P_0 = " + str(price_from_supply(housing_supply+Q_V)/PRICE_TO_RENT))
V = price_from_supply(housing_supply+Q_V) - (needed_price_shift * med_price)

print("V = " + str(V / PRICE_TO_RENT)) #Pigouvian tax



prices_tax = [p - (V/PRICE_TO_RENT) for p in prices]

plt.show()
p = sns.lineplot(x=supplies, y=prices)
p.set(title="Pittsburgh Housing Supply Curve")
p.set_xlabel("Supply Quantity (Q)")
p.set_ylabel("Price (P)")
sns.lineplot(x=supplies, y=prices_tax)
plt.show()

#Map

data = gpd.read_file("C:/Users/creek/Desktop/Ideathon/pittsburgh.geojson")
pops = []
for index, row in data.iterrows():
    try:
        pops.append(neighborhoods[row['name']])
    except KeyError:
        pops.append(0)

data['Newly affordable homes'] = pops
data.plot(column='Newly affordable homes').set(title="Newly affordable homes by neighborhood")
print(neighborhoods)
plt.show()