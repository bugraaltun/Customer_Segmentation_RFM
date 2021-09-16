#####################################################
######### CUSTOMER SEGMENTATION WITH RFM ##############
#####################################################

# Understanding and Preparing Data

import pandas as pd
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("Datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()

def check_df(dataframe, head=5):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(head))
    print("##################### Tail #####################")
    print(dataframe.tail(head))
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
    print("####################Describe ######################")
    print(df.describe().T)

check_df(df)
"""
##################### Shape #####################
(541910, 8)
##################### Types #####################
Invoice                object
StockCode              object
Description            object
Quantity                int64
InvoiceDate    datetime64[ns]
Price                 float64
Customer ID           float64
Country                object
dtype: object
##################### Head #####################
  Invoice StockCode                          Description  Quantity  \
0  536365    85123A   WHITE HANGING HEART T-LIGHT HOLDER         6   
1  536365     71053                  WHITE METAL LANTERN         6   
2  536365    84406B       CREAM CUPID HEARTS COAT HANGER         8   
3  536365    84029G  KNITTED UNION FLAG HOT WATER BOTTLE         6   
4  536365    84029E       RED WOOLLY HOTTIE WHITE HEART.         6   
          InvoiceDate   Price  Customer ID         Country  
0 2010-12-01 08:26:00 2.55000  17850.00000  United Kingdom  
1 2010-12-01 08:26:00 3.39000  17850.00000  United Kingdom  
2 2010-12-01 08:26:00 2.75000  17850.00000  United Kingdom  
3 2010-12-01 08:26:00 3.39000  17850.00000  United Kingdom  
4 2010-12-01 08:26:00 3.39000  17850.00000  United Kingdom  
##################### Tail #####################
       Invoice StockCode                      Description  Quantity  \
541905  581587     22899     CHILDREN'S APRON DOLLY GIRL          6   
541906  581587     23254    CHILDRENS CUTLERY DOLLY GIRL          4   
541907  581587     23255  CHILDRENS CUTLERY CIRCUS PARADE         4   
541908  581587     22138    BAKING SET 9 PIECE RETROSPOT          3   
541909  581587      POST                          POSTAGE         1   
               InvoiceDate    Price  Customer ID Country  
541905 2011-12-09 12:50:00  2.10000  12680.00000  France  
541906 2011-12-09 12:50:00  4.15000  12680.00000  France  
541907 2011-12-09 12:50:00  4.15000  12680.00000  France  
541908 2011-12-09 12:50:00  4.95000  12680.00000  France  
541909 2011-12-09 12:50:00 18.00000  12680.00000  France  
##################### NA #####################
Invoice             0
StockCode           0
Description      1454
Quantity            0
InvoiceDate         0
Price               0
Customer ID    135080
Country             0
dtype: int64
##################### Quantiles #####################
                 0.00000     0.05000     0.50000     0.95000     0.99000  \
Quantity    -80995.00000     1.00000     3.00000    29.00000   100.00000   
Price       -11062.06000     0.42000     2.08000     9.95000    18.00000   
Customer ID  12346.00000 12626.00000 15152.00000 17905.00000 18212.00000   
                1.00000  
Quantity    80995.00000  
Price       38970.00000  
Customer ID 18287.00000  
####################Describe ######################
                   count        mean        std          min         25%  \
Quantity    541910.00000     9.55223  218.08096 -80995.00000     1.00000   
Price       541910.00000     4.61114   96.75977 -11062.06000     1.25000   
Customer ID 406830.00000 15287.68416 1713.60307  12346.00000 13953.00000   
                    50%         75%         max  
Quantity        3.00000    10.00000 80995.00000  
Price           2.08000     4.13000 38970.00000  
Customer ID 15152.00000 16791.00000 18287.00000  
"""

#null columns
df.isnull().sum()
"""
Description      1454
Customer ID    135080
"""

#Removing missing observations
df.dropna(inplace = True)

#Number of unique products
df["Description"].nunique()

#Sorting the 5 most ordered products from most to least
df.groupby("Description").agg({"Quantity" : "sum"}).sort_values(by="Quantity", ascending=False).head(5)
#'C' in the #invoices shows the canceled transactions. Removing canceled transactions from the dataset.
df = df[~df["Invoice"].str.contains("C", na=False)]
df.head(30)
#Total Price
df["Total Price"] == df["Quantity"] * df["Price"]

#RFM metrics
df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby("Customer ID").agg({"InvoiceDate" : lambda date: (today_date - date.max()).days ,
                                     "Invoice" : lambda num: num.nunique(),
                                     "Total Price" : lambda price : price.sum()})
rfm.head()

rfm.columns = ["Recency","Frequency","Monetary"]
rfm = rfm[(rfm["Monetary"] > 0 )]

#Generating #RFM scores and converting them to a single variable

rfm["recency_score"] = pd.qcut(rfm["Recency"] , 5, labels=[5,4,3,2,1])
rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first") , 5 ,labels=[1,2,3,4,5])
rfm["monetary_score"] = pd.qcut(rfm["Monetary"],5 , labels=[1,2,3,4,5])

rfm["RFM_Score"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))
rfm.head()

#Defining #RFM scores as segments


seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["Segment"] = rfm["RFM_Score"].replace(seg_map, regex=True)
rfm.head()

rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])


new_df = pd.DataFrame()
new_df["loyal_customers_id"] = rfm[rfm["Segment"] == "loyal_customers"].index
new_df.to_csv("loyal_customers.csv")



