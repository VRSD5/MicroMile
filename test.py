import noaa_sdk


noaa = noaa_sdk.NOAA()

observations = noaa.get_observations("53202", "US")
cw = next(observations)

print(cw["icon"])
print(cw["textDescription"])
print(cw["temperature"]["value"])
print(cw["temperature"]["unitCode"][-1])
