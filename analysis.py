import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


# ==========================================
# 1. قراءة بيانات الإضاءة
# ==========================================

light_data = pd.read_excel(
    "data/cleaned/Baghdad_VIIRS_Hackathon_Winner_Cleaned (2).xlsx"
)

print("حجم البيانات:")
print(light_data.shape)

print("\nأسماء الأعمدة:")
print(light_data.columns)

print("\nالقيم الفارغة:")
print(light_data.isnull().sum())

print("\nالتكرارات:")
print(light_data.duplicated().sum())


# ==========================================
# 2. معلومات إحصائية عن بيانات الإضاءة
# ==========================================

print("\nالإحصائيات:")
print(light_data.describe())


# ==========================================
# 3. تحويل بيانات الإضاءة إلى نقاط جغرافية
# ==========================================

light_points = gpd.GeoDataFrame(
    light_data,
    geometry=gpd.points_from_xy(
        light_data["Longitude"],
        light_data["Latitude"]
    ),
    crs="EPSG:4326"
)


# ==========================================
# 4. قراءة حدود بغداد
# ==========================================

iraq = gpd.read_file("data/irq_admin2.shp")


# ==========================================
# 5. استخراج أقضية بغداد
# ==========================================

baghdad_districts = iraq[
    iraq["adm1_name"].str.contains(
        "Baghdad",
        case=False,
        na=False
    )
]

print("\nأقضية بغداد:")
print(
    baghdad_districts[
        ["adm1_name", "adm2_name"]
    ]
)


# ==========================================
# 6. رسم خريطة بغداد الأساسية
# ==========================================

fig, ax = plt.subplots(figsize=(10, 10))

baghdad_districts.plot(
    ax=ax,
    color="#f0f0f0",
    edgecolor="black",
    linewidth=1
)

for _, row in baghdad_districts.iterrows():

    centroid = row.geometry.centroid

    ax.annotate(
        text=row["adm2_name"],
        xy=(centroid.x, centroid.y),
        ha="center",
        fontsize=7,
        color="navy"
    )

plt.title("Baghdad Districts - Dark Sky Base Map")

plt.tight_layout()

plt.savefig(
    "baghdad_districts_map.png",
    dpi=300
)

plt.show()


# ==========================================
# 7. ربط نقاط الإضاءة بأقضية بغداد
# ==========================================

joined = gpd.sjoin(
    light_points,
    baghdad_districts[
        ["adm2_name", "geometry"]
    ],
    how="left",
    predicate="within"
)


# ==========================================
# 8. فحص النقاط التي لم ترتبط بأي قضاء
# ==========================================

not_matched = joined["adm2_name"].isna().sum()

print("\nالنقاط غير المرتبطة بأي قضاء:")
print(not_matched)


# ==========================================
# 9. حساب إحصائيات الإضاءة لكل قضاء
# ==========================================

district_summary = joined.groupby(
    "adm2_name"
)["avg_rad"].agg(
    ["count", "mean", "min", "max"]
).reset_index()

print("\nإحصائيات الإضاءة حسب القضاء:")
print(district_summary)


# ==========================================
# 10. رسم متوسط الإضاءة لكل قضاء
# ==========================================

plt.figure(figsize=(10, 6))

plt.bar(
    district_summary["adm2_name"],
    district_summary["mean"]
)

plt.xlabel("Baghdad District")

plt.ylabel("Average Light Intensity (avg_rad)")

plt.title(
    "Average Light Pollution by Baghdad District"
)

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "district_light_pollution.png",
    dpi=300
)

plt.show()


# ==========================================
# انتهى التحليل الأول
# ==========================================

print("\nتم تنفيذ التحليل بنجاح.")
print("تم حفظ:")
print("- baghdad_districts_map.png")
print("- district_light_pollution.png")
# ==========================================
# 11. فحص النقاط غير المرتبطة بالأقضية
# ==========================================

unmatched = joined[joined["adm2_name"].isna()]

print("\nعدد النقاط غير المرتبطة:")
print(len(unmatched))

print("\nالمناطق Region للنقاط غير المرتبطة:")
print(unmatched["Region"].value_counts())

print("\nأمثلة من النقاط غير المرتبطة:")
print(
    unmatched[
        ["Latitude", "Longitude", "avg_rad", "Region"]
    ].head(20)
)
# ==========================================
# 12. فحص جميع المناطق الموجودة في البيانات
# ==========================================

print("\nجميع المناطق الموجودة في بيانات الإضاءة:")

print(
    light_data["Region"].value_counts()
)
# ==========================================
# 13. جميع المناطق الموجودة في ملف GIS
# ==========================================

print("\nجميع الوحدات الإدارية في ملف GIS:")

print(
    iraq["adm2_name"].dropna().unique()
)
# ==========================================
# 14. خريطة شدة التلوث الضوئي في بغداد
# ==========================================

fig, ax = plt.subplots(figsize=(12, 10))

# رسم حدود بغداد
baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

# رسم نقاط الإضاءة
light_points.plot(
    ax=ax,
    column="avg_rad",
    cmap="inferno",
    markersize=8,
    alpha=0.7,
    legend=True,
    legend_kwds={
        "label": "Light Intensity (avg_rad)",
        "shrink": 0.7
    }
)

plt.title(
    "Baghdad Light Pollution Map - VIIRS Nighttime Lights"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    "baghdad_light_pollution_map.png",
    dpi=300
)

plt.show()

print("\nتم حفظ خريطة التلوث الضوئي:")
print("baghdad_light_pollution_map.png")
# ==========================================
# 15. توزيع تصنيفات Bortle
# ==========================================

print("\nتوزيع Bortle Class:")

print(
    light_data["Bortle_Class"].value_counts()
)
# ==========================================
# 16. العلاقة بين شدة الإضاءة و Bortle Class
# ==========================================

bortle_summary = light_data.groupby(
    "Bortle_Class"
)["avg_rad"].agg(
    ["count", "mean", "min", "max"]
).reset_index()

print("\nشدة الإضاءة حسب Bortle Class:")
print(bortle_summary)


# ==========================================
# 17. رسم متوسط الإضاءة حسب Bortle Class
# ==========================================

plt.figure(figsize=(10, 6))

plt.bar(
    bortle_summary["Bortle_Class"],
    bortle_summary["mean"]
)

plt.xlabel("Bortle Class")

plt.ylabel("Average Light Intensity (avg_rad)")

plt.title(
    "Average VIIRS Light Intensity by Bortle Class"
)

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    "bortle_light_intensity.png",
    dpi=300
)

plt.show()

print("\nتم حفظ الرسم:")
print("bortle_light_intensity.png")
# ==========================================
# 18. اكتشاف مناطق الإضاءة العالية Hotspots
# ==========================================

hotspot_threshold = light_data["avg_rad"].quantile(0.90)

hotspots = light_data[
    light_data["avg_rad"] >= hotspot_threshold
]

print("\nحد Hotspots - أعلى 10% من الإضاءة:")
print(hotspot_threshold)

print("\nعدد نقاط Hotspots:")
print(len(hotspots))

print("\nنسبة Hotspots من جميع البيانات:")
print(len(hotspots) / len(light_data) * 100)


# ==========================================
# 19. توزيع Hotspots حسب Region
# ==========================================

hotspot_regions = hotspots["Region"].value_counts()

print("\nHotspots حسب المنطقة:")
print(hotspot_regions)


# ==========================================
# 20. خريطة Hotspots
# ==========================================

hotspot_points = gpd.GeoDataFrame(
    hotspots,
    geometry=gpd.points_from_xy(
        hotspots["Longitude"],
        hotspots["Latitude"]
    ),
    crs="EPSG:4326"
)

fig, ax = plt.subplots(figsize=(12, 10))

baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

hotspot_points.plot(
    ax=ax,
    color="red",
    markersize=10,
    alpha=0.7
)

plt.title(
    "High Light Pollution Hotspots - Baghdad"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    "baghdad_light_hotspots.png",
    dpi=300
)

plt.show()

print("\nتم حفظ خريطة Hotspots:")
print("baghdad_light_hotspots.png")
# ==========================================
# 21. نسبة Hotspots داخل كل Region
# ==========================================

region_total = light_data["Region"].value_counts()

region_hotspots = hotspots["Region"].value_counts()

hotspot_density = pd.DataFrame({
    "Total_Points": region_total,
    "Hotspots": region_hotspots
}).fillna(0)

hotspot_density["Hotspot_Percentage"] = (
    hotspot_density["Hotspots"]
    / hotspot_density["Total_Points"]
    * 100
)

hotspot_density = hotspot_density.sort_values(
    "Hotspot_Percentage",
    ascending=False
)

print("\nنسبة Hotspots داخل كل منطقة:")
print(hotspot_density)


# ==========================================
# 22. رسم نسبة Hotspots
# ==========================================

plt.figure(figsize=(12, 7))

plt.bar(
    hotspot_density.index,
    hotspot_density["Hotspot_Percentage"]
)

plt.xlabel("Region")
plt.ylabel("Hotspots Percentage (%)")

plt.title(
    "Hotspot Density by Region - Baghdad"
)

plt.xticks(rotation=45, ha="right")

plt.tight_layout()

plt.savefig(
    "hotspot_density_by_region.png",
    dpi=300
)

plt.show()

print("\nتم حفظ الرسم:")
print("hotspot_density_by_region.png")
# ==========================================
# 23. تحليل Dark Sky Suitability
# ==========================================

print("\nتوزيع Dark Sky Suitability:")
print(
    light_data["DarkSky_Suitability"].value_counts()
)


print("\nDark Sky Suitability حسب Bortle Class:")
print(
    pd.crosstab(
        light_data["Bortle_Class"],
        light_data["DarkSky_Suitability"]
    )
)


print("\nDark Sky Suitability حسب Region:")
print(
    pd.crosstab(
        light_data["Region"],
        light_data["DarkSky_Suitability"]
    )
)
# ==========================================
# 24. Spatial Hotspot Clustering باستخدام DBSCAN
# ==========================================

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


# نستخدم الإحداثيات + شدة الإضاءة
cluster_data = light_data[
    ["Latitude", "Longitude", "avg_rad"]
].copy()


# توحيد المقاييس
X = StandardScaler().fit_transform(cluster_data)


# إنشاء نموذج DBSCAN
dbscan = DBSCAN(
    eps=0.18,
    min_samples=20
)


cluster_labels = dbscan.fit_predict(X)


# إضافة رقم المجموعة للبيانات
light_data["Cluster"] = cluster_labels


# ==========================================
# 25. نتائج Clustering
# ==========================================

print("\nنتائج DBSCAN:")
print(
    light_data["Cluster"].value_counts().sort_index()
)


print("\nعدد المجموعات المكتشفة:")
print(
    len(set(cluster_labels)) - (
        1 if -1 in cluster_labels else 0
    )
)


print("\nعدد النقاط التي اعتبرها DBSCAN Noise:")
print(
    (cluster_labels == -1).sum()
)


# ==========================================
# 26. متوسط الإضاءة لكل Cluster
# ==========================================

cluster_summary = light_data[
    light_data["Cluster"] != -1
].groupby("Cluster")["avg_rad"].agg(
    ["count", "mean", "min", "max"]
).reset_index()

print("\nمتوسط الإضاءة داخل كل Cluster:")
print(cluster_summary)


# ==========================================
# 27. خريطة Clusters
# ==========================================

cluster_points = gpd.GeoDataFrame(
    light_data[
        light_data["Cluster"] != -1
    ],
    geometry=gpd.points_from_xy(
        light_data[
            light_data["Cluster"] != -1
        ]["Longitude"],
        light_data[
            light_data["Cluster"] != -1
        ]["Latitude"]
    ),
    crs="EPSG:4326"
)


fig, ax = plt.subplots(figsize=(12, 10))

baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

cluster_points.plot(
    ax=ax,
    column="Cluster",
    categorical=True,
    markersize=8,
    alpha=0.7,
    legend=True
)

plt.title(
    "Spatial Clustering of Light Pollution - Baghdad"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    "baghdad_light_clusters.png",
    dpi=300
)

plt.show()

print("\nتم حفظ خريطة Clusters:")
print("baghdad_light_clusters.png")
print("\nعدد التواريخ المختلفة:")
print(light_data["Date"].nunique())

print("\nالتواريخ الموجودة:")
print(light_data["Date"].value_counts().sort_index()) 
print("\nالفترة الزمنية للبيانات:")
print(light_data["Date"].min(), "إلى", light_data["Date"].max())

print("عدد الأشهر:", light_data["Date"].nunique())
# ==========================================
# 28. التحليل الزمني للتلوث الضوئي
# ==========================================

monthly_summary = light_data.groupby("Date")["avg_rad"].agg(
    ["count", "mean", "min", "max"]
).reset_index()

print("\nالتحليل الشهري للإضاءة:")
print(monthly_summary)

# ==========================================
# 29. رسم التغير الزمني
# ==========================================

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_summary["Date"],
    monthly_summary["mean"],
    marker="o"
)

plt.xlabel("Date")
plt.ylabel("Average Light Intensity (avg_rad)")

plt.title(
    "Monthly Light Intensity in Baghdad (2022-2024)"
)

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "baghdad_light_temporal_trend.png",
    dpi=300
)

plt.show()

print("\nتم حفظ الرسم:")
print("baghdad_light_temporal_trend.png")
# ==========================================
# 30. مقارنة الإضاءة بين السنوات
# ==========================================

light_data["Year"] = pd.to_datetime(
    light_data["Date"]
).dt.year

yearly_summary = light_data.groupby("Year")["avg_rad"].agg(
    ["count", "mean", "min", "max"]
).reset_index()

print("\nالتحليل السنوي للإضاءة:")
print(yearly_summary)

# ==========================================
# 31. رسم المقارنة السنوية
# ==========================================

plt.figure(figsize=(8, 6))

plt.bar(
    yearly_summary["Year"].astype(str),
    yearly_summary["mean"]
)

plt.xlabel("Year")
plt.ylabel("Average Light Intensity (avg_rad)")

plt.title(
    "Annual Light Intensity in Baghdad (2022-2024)"
)

plt.tight_layout()

plt.savefig(
    "baghdad_annual_light_comparison.png",
    dpi=300
)

plt.show()

print("\nتم حفظ الرسم:")
print("baghdad_annual_light_comparison.png")
# ==========================================
# 32. فحص ثبات المواقع عبر الزمن
# ==========================================

location_count = light_data.groupby(
    ["Latitude", "Longitude"]
)["Date"].nunique()

print("\nعدد المواقع الفريدة:")
print(location_count.nunique())

print("\nعدد المواقع التي ظهرت في جميع الأشهر:")
print((location_count == 36).sum())

print("\nإجمالي المواقع الفريدة:")
print(len(location_count))
# ==========================================
# 33. فحص دقة الإحداثيات عبر الزمن
# ==========================================

print("\nعدد قيم Latitude المختلفة:")
print(light_data["Latitude"].nunique())

print("\nعدد قيم Longitude المختلفة:")
print(light_data["Longitude"].nunique())

print("\nأول 20 إحداثي:")
print(
    light_data[
        ["Latitude", "Longitude", "Date", "avg_rad"]
    ].head(20)
)
# ==========================================
# 34. عدد نقاط القياس في كل شهر
# ==========================================

monthly_count = light_data.groupby("Date").size()

print("\nعدد نقاط القياس لكل شهر:")
print(monthly_count)

print("\nأقل عدد نقاط في شهر:")
print(monthly_count.min())

print("\nأعلى عدد نقاط في شهر:")
print(monthly_count.max())
# ==========================================
# 35. تحديد نطاق منطقة الدراسة
# ==========================================

print("\nنطاق Latitude:")
print(
    light_data["Latitude"].min(),
    "إلى",
    light_data["Latitude"].max()
)

print("\nنطاق Longitude:")
print(
    light_data["Longitude"].min(),
    "إلى",
    light_data["Longitude"].max()
)
# ==========================================
# 36. إنشاء Grid مكاني لبغداد
# ==========================================

grid_size = 0.01

light_data["Grid_Lat"] = (
    light_data["Latitude"] // grid_size
) * grid_size

light_data["Grid_Lon"] = (
    light_data["Longitude"] // grid_size
) * grid_size

print("\nعدد خلايا Grid الفريدة:")
print(
    light_data[
        ["Grid_Lat", "Grid_Lon"]
    ].drop_duplicates().shape[0]
)

print("\nأول 10 خلايا:")
print(
    light_data[
        ["Grid_Lat", "Grid_Lon"]
    ].drop_duplicates().head(10)
)
# ==========================================
# 37. متوسط الإضاءة لكل Grid ولكل شهر
# ==========================================

grid_monthly = light_data.groupby(
    ["Grid_Lat", "Grid_Lon", "Date"]
)["avg_rad"].mean().reset_index()

print("\nحجم بيانات Grid الشهرية:")
print(grid_monthly.shape)

print("\nأول 20 صف:")
print(grid_monthly.head(20))
# ==========================================
# 38. ثبات خلايا Grid عبر الزمن
# ==========================================

grid_presence = grid_monthly.groupby(
    ["Grid_Lat", "Grid_Lon"]
)["Date"].nunique()

print("\nعدد الخلايا الفريدة:")
print(len(grid_presence))

print("\nأقل عدد أشهر ظهرت فيها الخلية:")
print(grid_presence.min())

print("\nأعلى عدد أشهر ظهرت فيها الخلية:")
print(grid_presence.max())

print("\nعدد الخلايا التي ظهرت في 12 شهر أو أكثر:")
print((grid_presence >= 12).sum())

print("\nعدد الخلايا التي ظهرت في جميع الأشهر:")
print((grid_presence == 36).sum())
# ==========================================
# 39. اختيار الخلايا المناسبة للتحليل الزمني
# ==========================================

stable_grids = grid_presence[
    grid_presence >= 12
].reset_index()

print("\nعدد الخلايا المختارة للتحليل الزمني:")
print(len(stable_grids))

print("\nأول 10 خلايا مختارة:")
print(stable_grids.head(10))
# ==========================================
# 40. فحص تغطية Grid حسب السنوات
# ==========================================

grid_year_presence = light_data.groupby(
    ["Grid_Lat", "Grid_Lon", "Year"]
)["Date"].nunique().reset_index()

year_coverage = grid_year_presence.groupby(
    ["Grid_Lat", "Grid_Lon"]
)["Year"].nunique()

print("\nعدد خلايا Grid التي ظهرت في السنوات الثلاث:")
print((year_coverage == 3).sum())

print("\nعدد الخلايا التي ظهرت في سنتين:")
print((year_coverage == 2).sum())

print("\nعدد الخلايا التي ظهرت في سنة واحدة فقط:")
print((year_coverage == 1).sum())
# ==========================================
# 41. مقارنة الإضاءة بين 2022 و 2024
# ==========================================

# اختيار الخلايا التي ظهرت في السنوات الثلاث
stable_year_grids = year_coverage[
    year_coverage == 3
].reset_index()

# أخذ بيانات هذه الخلايا فقط
stable_data = light_data.merge(
    stable_year_grids[
        ["Grid_Lat", "Grid_Lon"]
    ],
    on=["Grid_Lat", "Grid_Lon"],
    how="inner"
)

# متوسط الإضاءة لكل خلية في كل سنة
grid_yearly = stable_data.groupby(
    ["Grid_Lat", "Grid_Lon", "Year"]
)["avg_rad"].mean().reset_index()

# تحويل السنوات إلى أعمدة
grid_change = grid_yearly.pivot(
    index=["Grid_Lat", "Grid_Lon"],
    columns="Year",
    values="avg_rad"
).reset_index()

# حساب التغير بين 2022 و 2024
grid_change["Change"] = (
    grid_change[2024] -
    grid_change[2022]
)

# حساب نسبة التغير
grid_change["Percent_Change"] = (
    grid_change["Change"] /
    grid_change[2022]
) * 100

print("\nعدد الخلايا في تحليل التغير:")
print(len(grid_change))

print("\nأول 10 نتائج:")
print(grid_change.head(10))
# ==========================================
# 42. الملخص العام لتغير الإضاءة 2022 → 2024
# ==========================================

print("\nمتوسط الإضاءة في 2022:")
print(grid_change[2022].mean())

print("\nمتوسط الإضاءة في 2024:")
print(grid_change[2024].mean())

print("\nمتوسط مقدار التغير:")
print(grid_change["Change"].mean())

print("\nمتوسط نسبة التغير:")
print(grid_change["Percent_Change"].mean())

print("\nعدد الخلايا التي زادت إضاءتها:")
print((grid_change["Change"] > 0).sum())

print("\nعدد الخلايا التي انخفضت إضاءتها:")
print((grid_change["Change"] < 0).sum())

print("\nعدد الخلايا التي لم تتغير:")
print((grid_change["Change"] == 0).sum())
# ==========================================
# 43. خريطة تغير الإضاءة 2022 → 2024
# ==========================================

# ==========================================
# 43. خريطة تغير الإضاءة 2022 → 2024
# ==========================================

import geopandas as gpd
import matplotlib.pyplot as plt

# تحويل خلايا Grid إلى نقاط جغرافية
grid_change_geo = gpd.GeoDataFrame(
    grid_change,
    geometry=gpd.points_from_xy(
        grid_change["Grid_Lon"],
        grid_change["Grid_Lat"]
    ),
    crs="EPSG:4326"
)

# إنشاء الخريطة
fig, ax = plt.subplots(figsize=(12, 10))

# حدود بغداد
baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

# خلايا التغير
grid_change_geo.plot(
    ax=ax,
    column="Change",
    cmap="RdBu_r",
    markersize=25,
    legend=True,
    legend_kwds={
        "label": "Change in Light Intensity (2022 → 2024)",
        "shrink": 0.7
    }
)

plt.title("Change in Baghdad Light Pollution: 2022 → 2024")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    "baghdad_light_change_2022_2024.png",
    dpi=300
)

plt.show()

print("\nتم حفظ خريطة تغير الإضاءة:")
print("baghdad_light_change_2022_2024.png")
# ==========================================
# 44. أكبر التغيرات في الإضاءة
# ==========================================

print("\nأكبر 10 خلايا زادت إضاءتها:")
print(
    grid_change.sort_values(
        "Change",
        ascending=False
    )[
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2024,
            "Change",
            "Percent_Change"
        ]
    ].head(10)
)

print("\nأكبر 10 خلايا انخفضت إضاءتها:")
print(
    grid_change.sort_values(
        "Change",
        ascending=True
    )[
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2024,
            "Change",
            "Percent_Change"
        ]
    ].head(10)
)
# ==========================================
# 45. فحص اتجاه تغير الإضاءة عبر السنوات
# ==========================================

grid_change["Trend"] = "متذبذب"

# زيادة مستمرة
grid_change.loc[
    (grid_change[2022] < grid_change[2023]) &
    (grid_change[2023] < grid_change[2024]),
    "Trend"
] = "زيادة مستمرة"

# انخفاض مستمر
grid_change.loc[
    (grid_change[2022] > grid_change[2023]) &
    (grid_change[2023] > grid_change[2024]),
    "Trend"
] = "انخفاض مستمر"

# ارتفاع ثم انخفاض
grid_change.loc[
    (grid_change[2022] < grid_change[2023]) &
    (grid_change[2023] > grid_change[2024]),
    "Trend"
] = "ارتفاع ثم انخفاض"

# انخفاض ثم ارتفاع
grid_change.loc[
    (grid_change[2022] > grid_change[2023]) &
    (grid_change[2023] < grid_change[2024]),
    "Trend"
] = "انخفاض ثم ارتفاع"

print("\nأنواع الاتجاهات:")
print(grid_change["Trend"].value_counts())

print("\nنسبة كل اتجاه:")
print(
    grid_change["Trend"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)
# ==========================================
# 46. تحديد مناطق الزيادة المستمرة
# ==========================================

increasing_cells = grid_change[
    grid_change["Trend"] == "زيادة مستمرة"
].copy()

print("\nعدد الخلايا ذات الزيادة المستمرة:")
print(len(increasing_cells))

print("\nمتوسط الإضاءة في 2022:")
print(increasing_cells[2022].mean())

print("\nمتوسط الإضاءة في 2024:")
print(increasing_cells[2024].mean())

print("\nمتوسط مقدار الزيادة:")
print(increasing_cells["Change"].mean())

print("\nمتوسط نسبة الزيادة:")
print(increasing_cells["Percent_Change"].mean())

print("\nأكبر 10 خلايا ذات زيادة مستمرة:")
print(
    increasing_cells.sort_values(
        "Change",
        ascending=False
    )[
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2023,
            2024,
            "Change",
            "Percent_Change"
        ]
    ].head(10)
)
# ==========================================
# 47. خريطة مناطق الزيادة المستمرة
# ==========================================

increasing_cells_geo = gpd.GeoDataFrame(
    increasing_cells,
    geometry=gpd.points_from_xy(
        increasing_cells["Grid_Lon"],
        increasing_cells["Grid_Lat"]
    ),
    crs="EPSG:4326"
)

fig, ax = plt.subplots(figsize=(12, 10))

baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

increasing_cells_geo.plot(
    ax=ax,
    column="Percent_Change",
    cmap="Reds",
    markersize=30,
    legend=True,
    legend_kwds={
        "label": "Continuous Increase (%)",
        "shrink": 0.7
    }
)

plt.title(
    "Baghdad Areas with Continuous Increase in Light Pollution"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    "baghdad_continuous_light_increase.png",
    dpi=300
)

plt.show()

print("\nتم حفظ الخريطة:")
print("baghdad_continuous_light_increase.png")
# ==========================================
# 48. تحديد الخلايا الأكثر ظلامًا
# ==========================================

dark_cells = grid_change[
    grid_change[2024].notna()
].copy()

dark_cells = dark_cells.sort_values(
    2024,
    ascending=True
)

print("\nأكثر 20 خلية ظلامًا في 2024:")
print(
    dark_cells[
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2023,
            2024,
            "Change",
            "Percent_Change"
        ]
    ].head(20)
)
# ==========================================
# 49. تحديد الخلايا المظلمة والمستقرة
# ==========================================

dark_threshold = grid_change[2024].quantile(0.10)

dark_stable = grid_change[
    grid_change[2024] <= dark_threshold
].copy()

print("\nحد الظلام - أقل 10%:")
print(dark_threshold)

print("\nعدد الخلايا المظلمة:")
print(len(dark_stable))

print("\nمتوسط الإضاءة في 2022:")
print(dark_stable[2022].mean())

print("\nمتوسط الإضاءة في 2023:")
print(dark_stable[2023].mean())

print("\nمتوسط الإضاءة في 2024:")
print(dark_stable[2024].mean())

print("\nأكثر 20 خلية ظلامًا:")
print(
    dark_stable.sort_values(
        2024,
        ascending=True
    )[
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2023,
            2024,
            "Change",
            "Percent_Change",
            "Trend"
        ]
    ].head(20)
)
# ==========================================
# 50. المناطق المظلمة والمستقرة
# ==========================================

dark_stable_final = dark_stable[
    dark_stable["Change"] <= 0
].copy()

print("\nعدد المناطق المظلمة والمستقرة:")
print(len(dark_stable_final))

print("\nمتوسط الإضاءة في 2022:")
print(dark_stable_final[2022].mean())

print("\nمتوسط الإضاءة في 2023:")
print(dark_stable_final[2023].mean())

print("\nمتوسط الإضاءة في 2024:")
print(dark_stable_final[2024].mean())

print("\nأكثر 20 منطقة مظلمة ومستقرة:")
print(
    dark_stable_final.sort_values(
        2024,
        ascending=True
    )[
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2023,
            2024,
            "Change",
            "Percent_Change",
            "Trend"
        ]
    ].head(20)
)
# ==========================================
# 51. خريطة المناطق المرشحة للسماء المظلمة
# ==========================================

dark_stable_geo = gpd.GeoDataFrame(
    dark_stable_final,
    geometry=gpd.points_from_xy(
        dark_stable_final["Grid_Lon"],
        dark_stable_final["Grid_Lat"]
    ),
    crs="EPSG:4326"
)

fig, ax = plt.subplots(figsize=(12, 10))

baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

dark_stable_geo.plot(
    ax=ax,
    column=2024,
    cmap="viridis",
    markersize=80,
    legend=True,
    legend_kwds={
        "label": "2024 Light Intensity (avg_rad)",
        "shrink": 0.7
    }
)

plt.title(
    "Candidate Dark-Sky Zones in Baghdad - 2024"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    "baghdad_candidate_dark_sky_zones.png",
    dpi=300
)

plt.show()

print("\nتم حفظ الخريطة:")
print("baghdad_candidate_dark_sky_zones.png")
# ==========================================
# 52. فحص جودة الرصد في المناطق المظلمة
# ==========================================

dark_quality = light_data.merge(
    dark_stable_final[
        ["Grid_Lat", "Grid_Lon"]
    ],
    on=["Grid_Lat", "Grid_Lon"],
    how="inner"
)

print("\nعدد القراءات في المناطق المظلمة:")
print(len(dark_quality))

print("\nمتوسط تغطية الرصد cf_cvg:")
print(dark_quality["cf_cvg"].mean())

print("\nأقل تغطية:")
print(dark_quality["cf_cvg"].min())

print("\nأعلى تغطية:")
print(dark_quality["cf_cvg"].max())

print("\nتوزيع cf_cvg:")
print(dark_quality["cf_cvg"].value_counts().sort_index())
# ==========================================
# 53. مقارنة جودة الرصد
# ==========================================

print("\nمتوسط cf_cvg في كامل البيانات:")
print(light_data["cf_cvg"].mean())

print("\nمتوسط cf_cvg في المناطق المرشحة للسماء المظلمة:")
print(dark_quality["cf_cvg"].mean())

print("\nالفرق بين المتوسطين:")
print(
    dark_quality["cf_cvg"].mean()
    - light_data["cf_cvg"].mean()
)
# ==========================================
# 54. فحص استمرارية المناطق المظلمة
# ==========================================

dark_stable_final["Low_2022"] = dark_stable_final[2022] <= 12.33
dark_stable_final["Low_2023"] = dark_stable_final[2023] <= 12.33
dark_stable_final["Low_2024"] = dark_stable_final[2024] <= 12.33

dark_stable_final["Low_All_Years"] = (
    dark_stable_final["Low_2022"] &
    dark_stable_final["Low_2023"] &
    dark_stable_final["Low_2024"]
)

print("\nعدد الخلايا المظلمة:")
print(len(dark_stable_final))

print("\nعدد الخلايا منخفضة الإضاءة في السنوات الثلاث:")
print(dark_stable_final["Low_All_Years"].sum())

print("\nالخلايا التي تحقق الشرط:")
print(
    dark_stable_final[
        dark_stable_final["Low_All_Years"]
    ][
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2023,
            2024,
            "Change",
            "Percent_Change",
            "Trend"
        ]
    ]
)
# ==========================================
# 55. فحص عدد الأشهر لكل خلية مرشحة
# ==========================================

candidate_grids = dark_stable_final[
    dark_stable_final["Low_All_Years"]
][
    ["Grid_Lat", "Grid_Lon"]
].copy()

candidate_presence = grid_monthly.merge(
    candidate_grids,
    on=["Grid_Lat", "Grid_Lon"],
    how="inner"
)

candidate_months = candidate_presence.groupby(
    ["Grid_Lat", "Grid_Lon"]
)["Date"].nunique().reset_index()

candidate_months = candidate_months.rename(
    columns={"Date": "Months_Observed"}
)

print("\nعدد الخلايا المرشحة:")
print(len(candidate_months))

print("\nعدد الأشهر المرصودة لكل خلية:")
print(
    candidate_months.sort_values(
        "Months_Observed",
        ascending=False
    )
)
# ==========================================
# 56. اختيار أقوى مناطق السماء المظلمة
# ==========================================

strong_candidates = dark_stable_final[
    dark_stable_final["Low_All_Years"]
].merge(
    candidate_months,
    on=["Grid_Lat", "Grid_Lon"],
    how="left"
)

strong_candidates = strong_candidates[
    strong_candidates["Months_Observed"] >= 12
].copy()

print("\nعدد المرشحين الأقوياء:")
print(len(strong_candidates))

print("\nالمرشحون الأقوياء:")
print(
    strong_candidates.sort_values(
        "Months_Observed",
        ascending=False
    )[
        [
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2023,
            2024,
            "Change",
            "Percent_Change",
            "Months_Observed",
            "Trend"
        ]
    ]
)
# ==========================================
# 57. فحص أعمدة المرشحين
# ==========================================

comparison = strong_candidates[
    [
        "Grid_Lat",
        "Grid_Lon",
        2022,
        2023,
        2024,
        "Change",
        "Percent_Change",
        "Months_Observed",
        "Trend"
    ]
].copy()

print("\nأسماء الأعمدة:")
print(comparison.columns.tolist())

print("\nبيانات المرشحين:")
print(comparison.to_string(index=False))
# ==========================================
# 57. ترتيب المرشحين حسب الإضاءة في 2024
# ==========================================

comparison = strong_candidates[
    [
        "Grid_Lat",
        "Grid_Lon",
        2022,
        2023,
        2024,
        "Change",
        "Percent_Change",
        "Months_Observed",
        "Trend"
    ]
].copy()

comparison = comparison.sort_values(
    by=2024,
    ascending=True
)

print("\nترتيب المرشحين من الأظلم إلى الأكثر إضاءة:")
print(comparison.to_string(index=False))
# ==========================================
# 58. تجميع الخلايا المرشحة المتجاورة
# ==========================================

candidate_points = comparison[
    ["Grid_Lat", "Grid_Lon"]
].values

groups = []
used = set()

for i in range(len(candidate_points)):

    if i in used:
        continue

    group = [i]
    used.add(i)

    for j in range(len(candidate_points)):

        if j in used:
            continue

        lat_diff = abs(
            candidate_points[i][0]
            - candidate_points[j][0]
        )

        lon_diff = abs(
            candidate_points[i][1]
            - candidate_points[j][1]
        )

        if lat_diff <= 0.02 and lon_diff <= 0.02:
            group.append(j)
            used.add(j)

    groups.append(group)

print("\nعدد المجموعات المرشحة:")
print(len(groups))

for number, group in enumerate(groups, start=1):

    print(f"\nالمجموعة {number}:")

    print(
        comparison.iloc[group][
            [
                "Grid_Lat",
                "Grid_Lon",
                2024,
                "Months_Observed"
            ]
        ].to_string(index=False)
    )
    # ==========================================
# 59. ملخص المجموعات المرشحة
# ==========================================

group_summary = []

for number, group in enumerate(groups, start=1):

    data = comparison.iloc[group]

    group_summary.append({
        "Group": number,
        "Cells": len(data),
        "Mean_2024": data[2024].mean(),
        "Min_2024": data[2024].min(),
        "Mean_Change": data["Change"].mean(),
        "Mean_Percent_Change": data["Percent_Change"].mean(),
        "Mean_Months_Observed": data["Months_Observed"].mean()
    })

group_summary = pd.DataFrame(group_summary)

print("\nملخص المجموعات المرشحة:")
print(
    group_summary.to_string(index=False)
)
# ==========================================
# 60. خريطة المجموعات المرشحة
# ==========================================

group_points = []

for number, group in enumerate(groups, start=1):

    data = comparison.iloc[group].copy()

    for _, row in data.iterrows():

        group_points.append({
            "Group": f"Group {number}",
            "Grid_Lat": row["Grid_Lat"],
            "Grid_Lon": row["Grid_Lon"],
            "Light_2024": row[2024],
            "Months_Observed": row["Months_Observed"]
        })

group_points = pd.DataFrame(group_points)

group_geo = gpd.GeoDataFrame(
    group_points,
    geometry=gpd.points_from_xy(
        group_points["Grid_Lon"],
        group_points["Grid_Lat"]
    ),
    crs="EPSG:4326"
)

fig, ax = plt.subplots(figsize=(12, 10))

# حدود مناطق بغداد
baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

# نقاط المجموعات
group_geo.plot(
    ax=ax,
    column="Group",
    markersize=140,
    legend=True,
    alpha=0.85
)

plt.title(
    "Candidate Dark-Sky Groups in Baghdad - 2024"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

plt.savefig(
    "baghdad_candidate_dark_sky_groups.png",
    dpi=300
)

plt.show()
# ==========================================
# 61. مركز كل مجموعة مرشحة
# ==========================================

group_centers = []

for number, group in enumerate(groups, start=1):

    data = comparison.iloc[group]

    center_lat = data["Grid_Lat"].mean()
    center_lon = data["Grid_Lon"].mean()

    group_centers.append({
        "Group": number,
        "Center_Lat": center_lat,
        "Center_Lon": center_lon,
        "Cells": len(data),
        "Mean_2024": data[2024].mean(),
        "Mean_Change": data["Change"].mean(),
        "Mean_Percent_Change": data["Percent_Change"].mean(),
        "Mean_Months_Observed": data["Months_Observed"].mean()
    })

group_centers = pd.DataFrame(group_centers)

print("\nمراكز المجموعات المرشحة:")
print(
    group_centers.to_string(index=False)
)
# ==========================================
# 62. الجدول النهائي للمناطق المرشحة
# ==========================================

final_candidates = group_centers.copy()

# ترتيب الأعمدة
final_candidates = final_candidates[
    [
        "Group",
        "Center_Lat",
        "Center_Lon",
        "Cells",
        "Mean_2024",
        "Mean_Change",
        "Mean_Percent_Change",
        "Mean_Months_Observed"
    ]
]

print("\nFinal Candidate Dark-Sky Groups:")
print(
    final_candidates.to_string(index=False)
)
# ==========================================
# 63. Final Candidate Dark-Sky Map
# ==========================================

fig, ax = plt.subplots(figsize=(12, 10))

# حدود بغداد
baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

# رسم خلايا المرشحين
for number, group in enumerate(groups, start=1):

    data = comparison.iloc[group]

    ax.scatter(
        data["Grid_Lon"],
        data["Grid_Lat"],
        s=180,
        label=f"Group {number}",
        alpha=0.85
    )

    # مركز المجموعة
    center_lat = data["Grid_Lat"].mean()
    center_lon = data["Grid_Lon"].mean()

    ax.text(
        center_lon,
        center_lat,
        f"G{number}",
        fontsize=12,
        fontweight="bold",
        ha="center",
        va="center"
    )

plt.title(
    "Candidate Dark-Sky Groups in Baghdad (2022–2024)"
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.legend(
    title="Candidate Groups"
)

plt.tight_layout()

plt.savefig(
    "baghdad_final_candidate_groups.png",
    dpi=300
)

plt.show()
# ==========================================
# 65. قياس التجانس داخل المجموعات
# ==========================================

group_consistency = []

for number, group in enumerate(groups, start=1):

    data = comparison.iloc[group]

    group_consistency.append({
        "Group": number,
        "Cells": len(data),
        "Mean_2024": data[2024].mean(),
        "Min_2024": data[2024].min(),
        "Max_2024": data[2024].max(),
        "Std_2024": data[2024].std() if len(data) > 1 else 0,
        "Mean_Months_Observed": data["Months_Observed"].mean()
    })

group_consistency = pd.DataFrame(group_consistency)

print("\nConsistency داخل المجموعات:")
print(
    group_consistency.to_string(index=False)
)
# ==========================================
# 66. الاستقرار الزمني للمجموعات
# ==========================================

group_temporal = []

for number, group in enumerate(groups, start=1):

    data = comparison.iloc[group]

    group_temporal.append({
        "Group": number,
        "Light_2022": data[2022].mean(),
        "Light_2023": data[2023].mean(),
        "Light_2024": data[2024].mean(),
        "Change_2022_2024": data["Change"].mean(),
        "Percent_Change": data["Percent_Change"].mean()
    })

group_temporal = pd.DataFrame(group_temporal)

print("\nالاستقرار الزمني للمجموعات:")
print(
    group_temporal.to_string(index=False)
)
# ==========================================
# 67. التحليل الشهري للمجموعات المرشحة
# ==========================================

# إنشاء جدول يربط كل خلية برقم المجموعة
group_cells = []

for number, group in enumerate(groups, start=1):

    data = comparison.iloc[group]

    for _, row in data.iterrows():

        group_cells.append({
            "Group": number,
            "Grid_Lat": row["Grid_Lat"],
            "Grid_Lon": row["Grid_Lon"]
        })

group_cells = pd.DataFrame(group_cells)

# ربط الخلايا بالبيانات الأصلية
group_monthly = light_data.merge(
    group_cells,
    on=["Grid_Lat", "Grid_Lon"],
    how="inner"
)

# المتوسط الشهري لكل مجموعة
group_monthly_avg = group_monthly.groupby(
    ["Group", "Date"]
)["avg_rad"].mean().reset_index()

print("\nعدد القراءات داخل المجموعات:")
print(group_monthly.groupby("Group").size())

print("\nأول نتائج التحليل الشهري:")
print(
    group_monthly_avg.head(20).to_string(index=False)
)
# ==============================
# Section 68: النمط الشهري للمجموعات
# ==============================

# تحويل Date إلى نوع تاريخ
group_monthly["Date"] = pd.to_datetime(
    group_monthly["Date"]
)

# استخراج رقم الشهر
group_monthly["Month"] = group_monthly["Date"].dt.month

# حساب متوسط الإضاءة لكل مجموعة في كل شهر
monthly_pattern = group_monthly.groupby(
    ["Group", "Month"]
)["avg_rad"].mean().reset_index()

# عرض النتائج
print("\nالنمط الشهري للمجموعات:")

print(
    monthly_pattern.to_string(index=False)
)
# ==============================
# Section 69: استقرار الإضاءة الشهرية
# ==============================

monthly_consistency = monthly_pattern.groupby(
    "Group"
)["avg_rad"].agg(
    Monthly_Mean="mean",
    Monthly_Min="min",
    Monthly_Max="max",
    Monthly_Std="std",
    Months_Available="count"
).reset_index()

print("\nاستقرار الإضاءة الشهرية للمجموعات:")

print(
    monthly_consistency.to_string(index=False)
)
# ==============================
# Section 70: مقارنة المرشحين مع خلايا بغداد المستقرة
# ==============================

# جميع الخلايا المستقرة التي عندها بيانات 2024
all_stable_2024 = grid_change[
    grid_change[2024].notna()
].copy()

# حساب الإحصائيات العامة لبغداد
baghdad_stats = {
    "Mean": all_stable_2024[2024].mean(),
    "Median": all_stable_2024[2024].median(),
    "10th_Percentile": all_stable_2024[2024].quantile(0.10),
    "25th_Percentile": all_stable_2024[2024].quantile(0.25),
    "Min": all_stable_2024[2024].min()
}

print("\nإحصائيات خلايا بغداد المستقرة - 2024:")

for key, value in baghdad_stats.items():
    print(f"{key}: {value:.2f}")


# مقارنة كل مجموعة مع متوسط بغداد
comparison_final = group_centers.copy()

comparison_final["Difference_From_Baghdad"] = (
    comparison_final["Mean_2024"]
    - baghdad_stats["Mean"]
)

comparison_final["Percent_Below_Baghdad"] = (
    (baghdad_stats["Mean"] - comparison_final["Mean_2024"])
    / baghdad_stats["Mean"]
    * 100
)

print("\nمقارنة المجموعات مع متوسط خلايا بغداد:")

print(
    comparison_final[
        [
            "Group",
            "Mean_2024",
            "Difference_From_Baghdad",
            "Percent_Below_Baghdad",
            "Cells",
            "Mean_Months_Observed"
        ]
    ].to_string(index=False)
)
# ==============================
# Section 71: Candidate Suitability Score
# ==============================

import numpy as np

# نبدأ من بيانات المجموعات النهائية
candidate_score = group_centers.copy()

# ------------------------------------------------
# 1. Light Score
# كلما كانت الإضاءة أقل → النقاط أعلى
# ------------------------------------------------

light_min = candidate_score["Mean_2024"].min()
light_max = candidate_score["Mean_2024"].max()

candidate_score["Light_Score"] = (
    (light_max - candidate_score["Mean_2024"])
    / (light_max - light_min)
    * 100
)

# ------------------------------------------------
# 2. Stability Score
# نستخدم الانحراف المعياري الشهري
# كلما كان التذبذب أقل → النقاط أعلى
# ------------------------------------------------

candidate_score = candidate_score.merge(
    monthly_consistency[
        [
            "Group",
            "Monthly_Std",
            "Months_Available"
        ]
    ],
    on="Group",
    how="left"
)

std_min = candidate_score["Monthly_Std"].min()
std_max = candidate_score["Monthly_Std"].max()

candidate_score["Stability_Score"] = (
    (std_max - candidate_score["Monthly_Std"])
    / (std_max - std_min)
    * 100
)

# ------------------------------------------------
# 3. Coverage Score
# عدد الأشهر المرصودة
# كلما زادت التغطية → النقاط أعلى
# ------------------------------------------------

coverage_min = candidate_score["Mean_Months_Observed"].min()
coverage_max = candidate_score["Mean_Months_Observed"].max()

candidate_score["Coverage_Score"] = (
    (candidate_score["Mean_Months_Observed"] - coverage_min)
    / (coverage_max - coverage_min)
    * 100
)

# ------------------------------------------------
# 4. Temporal Trend Score
# كلما كان التغير 2022 → 2024 أكثر انخفاضًا
# → النقاط أعلى
# ------------------------------------------------

change_min = candidate_score["Mean_Percent_Change"].min()
change_max = candidate_score["Mean_Percent_Change"].max()

candidate_score["Trend_Score"] = (
    (change_max - candidate_score["Mean_Percent_Change"])
    / (change_max - change_min)
    * 100
)

# ------------------------------------------------
# 5. Final Score
# ------------------------------------------------

candidate_score["Final_Score"] = (
    candidate_score["Light_Score"] * 0.40
    + candidate_score["Stability_Score"] * 0.25
    + candidate_score["Coverage_Score"] * 0.20
    + candidate_score["Trend_Score"] * 0.15
)

# ------------------------------------------------
# 6. ترتيب النتائج فقط لغرض المقارنة
# ------------------------------------------------

candidate_score = candidate_score.sort_values(
    by="Final_Score",
    ascending=False
)

# ------------------------------------------------
# 7. عرض النتيجة
# ------------------------------------------------

print("\n======================================")
print("Candidate Dark-Sky Suitability Score")
print("======================================")

print(
    candidate_score[
        [
            "Group",
            "Mean_2024",
            "Mean_Percent_Change",
            "Mean_Months_Observed",
            "Monthly_Std",
            "Light_Score",
            "Stability_Score",
            "Coverage_Score",
            "Trend_Score",
            "Final_Score"
        ]
    ].round(2).to_string(index=False)
)
# ==============================
# Section 72: Final Candidate Summary
# ==============================

final_summary = comparison[
    [
        "Grid_Lat",
        "Grid_Lon",
        2022,
        2023,
        2024,
        "Change",
        "Percent_Change",
        "Months_Observed",
        "Trend"
    ]
].copy()

# إضافة رقم المجموعة
group_map = {}

for number, group in enumerate(groups, start=1):
    for index in group:
        group_map[comparison.index[index]] = number

final_summary["Group"] = final_summary.index.map(group_map)

# إضافة الاستقرار الشهري
final_summary = final_summary.merge(
    monthly_consistency[
        [
            "Group",
            "Monthly_Mean",
            "Monthly_Min",
            "Monthly_Max",
            "Monthly_Std",
            "Months_Available"
        ]
    ],
    on="Group",
    how="left"
)

# ترتيب حسب المجموعة ثم الإضاءة في 2024
final_summary = final_summary.sort_values(
    ["Group", 2024]
)

print("\n======================================")
print("FINAL CANDIDATE DARK-SKY AREAS")
print("======================================")

print(
    final_summary[
        [
            "Group",
            "Grid_Lat",
            "Grid_Lon",
            2022,
            2023,
            2024,
            "Change",
            "Percent_Change",
            "Months_Observed",
            "Monthly_Std",
            "Trend"
        ]
    ].round(2).to_string(index=False)
)
# ==============================
# Section 73: Final Candidate Dark-Sky Map
# ==============================

# إنشاء GeoDataFrame للخلايا المرشحة
final_geo = gpd.GeoDataFrame(
    final_summary,
    geometry=gpd.points_from_xy(
        final_summary["Grid_Lon"],
        final_summary["Grid_Lat"]
    ),
    crs="EPSG:4326"
)

# إنشاء الخريطة
fig, ax = plt.subplots(figsize=(12, 10))

# رسم حدود مناطق بغداد
baghdad_districts.plot(
    ax=ax,
    facecolor="none",
    edgecolor="black",
    linewidth=1
)

# رسم الخلايا المرشحة
final_geo.plot(
    ax=ax,
    column="Group",
    markersize=180,
    legend=True,
    alpha=0.9
)

# كتابة اسم المجموعة بجانب كل نقطة
for _, row in final_geo.iterrows():

    ax.annotate(
        f"Group {int(row['Group'])}",
        xy=(row["Grid_Lon"], row["Grid_Lat"]),
        xytext=(6, 6),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold"
    )

# العنوان
plt.title(
    "Final Candidate Dark-Sky Areas in Baghdad",
    fontsize=16
)

plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()

# حفظ الخريطة
plt.savefig(
    "baghdad_final_candidate_areas.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nتم حفظ الخريطة النهائية:")
print("baghdad_final_candidate_areas.png")
# ==========================================
# Section 74: Final Scientific Check
# ==========================================

print("\n======================================")
print("FINAL SCIENTIFIC CHECK")
print("======================================")

# 1. حجم البيانات
print("\n1) Dataset:")
print("Rows:", len(light_data))
print("Columns:", len(light_data.columns))

# 2. Missing values
print("\n2) Missing values:")
print(light_data.isnull().sum())

# 3. Duplicates
print("\n3) Duplicate rows:")
print(light_data.duplicated().sum())

# 4. Date range
print("\n4) Date range:")
print("Start:", light_data["Date"].min())
print("End:", light_data["Date"].max())
print("Unique months:", light_data["Date"].nunique())

# 5. Light intensity
print("\n5) Light intensity:")
print("Minimum:", light_data["avg_rad"].min())
print("Maximum:", light_data["avg_rad"].max())
print("Mean:", light_data["avg_rad"].mean())

# 6. Geographic range
print("\n6) Geographic coverage:")
print("Latitude:", light_data["Latitude"].min(), "to", light_data["Latitude"].max())
print("Longitude:", light_data["Longitude"].min(), "to", light_data["Longitude"].max())

# 7. Candidate areas
print("\n7) Candidate areas:")
print("Groups:", final_summary["Group"].nunique())
print("Candidate cells:", len(final_summary))

# 8. Candidate readings
candidate_readings = light_data.merge(
    final_summary[["Grid_Lat", "Grid_Lon"]],
    on=["Grid_Lat", "Grid_Lon"],
    how="inner"
)

print("Candidate readings:", len(candidate_readings))

# 9. Candidate average
print("\n8) Candidate 2024 light intensity:")
print(
    final_summary.groupby("Group")[2024]
    .mean()
    .round(2)
)

# 10. Final check
print("\n======================================")
print("CHECK COMPLETE")
print("======================================")
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error


# 1. قراءة نفس بيانات المشروع
df = pd.read_excel(
    "data/cleaned/Baghdad_VIIRS_Hackathon_Winner_Cleaned (2).xlsx"
)


# 2. تحويل التاريخ واستخراج السنة والشهر
df["Date"] = pd.to_datetime(df["Date"])

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month


# 3. المتغيرات والهدف
features = [
    "Latitude",
    "Longitude",
    "Year",
    "Month",
    "cf_cvg"
]

target = "avg_rad"

X = df[features]
y = df[target]


# 4. تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# 5. تدريب النموذج
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# 6. التنبؤ
y_pred = model.predict(X_test)


# 7. التقييم
r2 = r2_score(y_test, y_pred)

mae = mean_absolute_error(
    y_test,
    y_pred
)


print("=" * 40)
print("DARKSKY AI - RANDOM FOREST")
print("=" * 40)

print(f"R^2 Score: {r2:.4f}")
print(f"MAE: {mae:.4f}")


# 8. أهمية المتغيرات
importances = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=True)

print("\nFeature Importance:")
print(importances)


# 9. الرسم
plt.figure(figsize=(8, 5))

importances.plot(kind="barh")

plt.title("Feature Importance - DarkSky AI")
plt.xlabel("Importance")

plt.tight_layout()

plt.savefig(
    "ml_feature_importance.png",
    dpi=300
)

plt.show()

print("\nتم حفظ الرسم:")
print("ml_feature_importance.png")
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error


# ==========================================
# 1. قراءة نفس بيانات المشروع
# ==========================================

df = pd.read_excel(
    "data/cleaned/Baghdad_VIIRS_Hackathon_Winner_Cleaned (2).xlsx"
)


# ==========================================
# 2. تجهيز التاريخ
# ==========================================

df["Date"] = pd.to_datetime(df["Date"])

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month


# ==========================================
# 3. المتغيرات والهدف
# ==========================================

features = [
    "Latitude",
    "Longitude",
    "Year",
    "Month",
    "cf_cvg"
]

target = "avg_rad"


# ==========================================
# 4. تدريب على 2022 و 2023
#    اختبار على 2024
# ==========================================

train_data = df[df["Year"] < 2024].copy()

test_data = df[df["Year"] == 2024].copy()


X_train = train_data[features]
y_train = train_data[target]

X_test = test_data[features]
y_test = test_data[target]


print("=" * 45)
print("DARKSKY AI - TIME BASED VALIDATION")
print("=" * 45)

print(f"Training rows: {len(train_data)}")
print(f"Testing rows: {len(test_data)}")


# ==========================================
# 5. تدريب Random Forest
# ==========================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# ==========================================
# 6. التنبؤ على 2024
# ==========================================

y_pred = model.predict(X_test)


# ==========================================
# 7. تقييم النموذج
# ==========================================

r2 = r2_score(y_test, y_pred)

mae = mean_absolute_error(
    y_test,
    y_pred
)


print("\nResults:")
print(f"R^2 Score: {r2:.4f}")
print(f"MAE: {mae:.4f}")


# ==========================================
# 8. مقارنة المتوسط الحقيقي والمتوقع
# ==========================================

print("\n2024 Mean:")
print(f"Actual avg_rad:    {y_test.mean():.4f}")
print(f"Predicted avg_rad: {y_pred.mean():.4f}")


print("\n========================================")
print("TIME BASED CHECK COMPLETE")
print("========================================")
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


# ==========================================
# 1. قراءة البيانات
# ==========================================

df = pd.read_excel(
    "data/cleaned/Baghdad_VIIRS_Hackathon_Winner_Cleaned (2).xlsx"
)


# ==========================================
# 2. تجهيز التاريخ
# ==========================================

df["Date"] = pd.to_datetime(df["Date"])

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month


# ==========================================
# 3. المتغيرات المستخدمة في ML
# ==========================================

features = [
    "Latitude",
    "Longitude",
    "Year",
    "Month",
    "cf_cvg"
]

target = "avg_rad"


# ==========================================
# 4. تدريب النموذج على 2022–2023 فقط
# ==========================================

train_data = df[df["Year"] < 2024].copy()

X_train = train_data[features]
y_train = train_data[target]


model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# ==========================================
# 5. المناطق المرشحة النهائية
# ==========================================

candidate_cells = pd.DataFrame({
    "Group": [1, 1, 1, 2, 3, 3, 4, 4],

    "Grid_Lat": [
        33.65,
        33.66,
        33.65,
        33.64,
        33.68,
        33.69,
        33.10,
        33.09
    ],

    "Grid_Lon": [
        44.39,
        44.39,
        44.40,
        44.37,
        44.37,
        44.38,
        44.56,
        44.57
    ]
})


# ==========================================
# 6. أخذ قراءات 2024 داخل المناطق المرشحة
# ==========================================

candidate_2024 = df[
    (df["Year"] == 2024)
].copy()


candidate_results = []


for _, cell in candidate_cells.iterrows():

    # نحدد القراءات القريبة من مركز الخلية
    cell_data = candidate_2024[
        (abs(candidate_2024["Latitude"] - cell["Grid_Lat"]) <= 0.005) &
        (abs(candidate_2024["Longitude"] - cell["Grid_Lon"]) <= 0.005)
    ].copy()

    if len(cell_data) == 0:
        continue

    # التنبؤ
    X_cell = cell_data[features]

    predictions = model.predict(X_cell)

    actual_mean = cell_data[target].mean()
    predicted_mean = predictions.mean()

    candidate_results.append({
        "Group": int(cell["Group"]),
        "Grid_Lat": cell["Grid_Lat"],
        "Grid_Lon": cell["Grid_Lon"],
        "Actual_2024_avg_rad": actual_mean,
        "Predicted_2024_avg_rad": predicted_mean,
        "Difference": actual_mean - predicted_mean,
        "Readings": len(cell_data)
    })


# ==========================================
# 7. النتائج
# ==========================================

results = pd.DataFrame(candidate_results)


print("=" * 60)
print("DARKSKY AI - ML CANDIDATE AREA VALIDATION")
print("=" * 60)

print(results.round(3).to_string(index=False))


# ==========================================
# 8. حفظ النتائج
# ==========================================

results.to_csv(
    "ml_candidate_area_results.csv",
    index=False
)


print("\nتم حفظ النتائج:")
print("ml_candidate_area_results.csv")

print("\n========================================")
print("CANDIDATE AREA ML CHECK COMPLETE")
print("========================================")
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


# ==========================================
# 1. قراءة نفس بيانات المشروع
# ==========================================

df = pd.read_excel(
    "data/cleaned/Baghdad_VIIRS_Hackathon_Winner_Cleaned (2).xlsx"
)


# ==========================================
# 2. تجهيز التاريخ
# ==========================================

df["Date"] = pd.to_datetime(df["Date"])

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month


# ==========================================
# 3. إنشاء نفس Grid المستخدم بالتحليل الأساسي
# ==========================================

grid_size = 0.01

df["Grid_Lat"] = (
    (df["Latitude"] // grid_size) * grid_size
).round(2)

df["Grid_Lon"] = (
    (df["Longitude"] // grid_size) * grid_size
).round(2)
# ==========================================
# 4. المتغيرات والهدف
# ==========================================

features = [
    "Latitude",
    "Longitude",
    "Year",
    "Month",
    "cf_cvg"
]

target = "avg_rad"


# ==========================================
# 5. تدريب ML على 2022 و2023 فقط
# ==========================================

train_data = df[df["Year"] < 2024].copy()

X_train = train_data[features]
y_train = train_data[target]


model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# ==========================================
# 6. الخلايا المرشحة النهائية
# ==========================================

candidate_cells = pd.DataFrame({
    "Group": [1, 1, 1, 2, 3, 3, 4, 4],

    "Grid_Lat": [
        33.65,
        33.66,
        33.65,
        33.64,
        33.68,
        33.69,
        33.10,
        33.09
    ],

    "Grid_Lon": [
        44.39,
        44.39,
        44.40,
        44.37,
        44.37,
        44.38,
        44.56,
        44.57
    ]
})


# ==========================================
# 7. أخذ بيانات 2024
# ==========================================

test_2024 = df[df["Year"] == 2024].copy()


results = []


# ==========================================
# 8. تحليل كل خلية بنفس Grid الأصلي
# ==========================================

for _, cell in candidate_cells.iterrows():

    cell_data = test_2024[
        (test_2024["Grid_Lat"] == cell["Grid_Lat"]) &
        (test_2024["Grid_Lon"] == cell["Grid_Lon"])
    ].copy()

    if len(cell_data) == 0:
        continue

    # توقع ML
    predictions = model.predict(
        cell_data[features]
    )

    actual_mean = cell_data[target].mean()
    predicted_mean = predictions.mean()

    results.append({
        "Group": int(cell["Group"]),
        "Grid_Lat": cell["Grid_Lat"],
        "Grid_Lon": cell["Grid_Lon"],
        "Actual_2024_avg_rad": actual_mean,
        "Predicted_2024_avg_rad": predicted_mean,
        "Difference": actual_mean - predicted_mean,
        "Readings": len(cell_data)
    })


# ==========================================
# 9. النتائج النهائية
# ==========================================

results = pd.DataFrame(results)


print("=" * 70)
print("DARKSKY AI - FINAL ML CANDIDATE VALIDATION")
print("=" * 70)

print(
    results.round(3).to_string(index=False)
)


# ==========================================
# 10. حفظ النتائج
# ==========================================

results.to_csv(
    "ml_final_candidate_validation.csv",
    index=False
)


print("\nتم حفظ النتائج:")
print("ml_final_candidate_validation.csv")


print("\n========================================")
print("FINAL ML VALIDATION COMPLETE")
print("========================================")