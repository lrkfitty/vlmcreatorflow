
print("DEBUG: characters_data keys:", list(characters_data.keys()))
if cast_selection:
    print("DEBUG: Selected:", cast_selection[0])
    print("DEBUG: Value in characters_data:", characters_data.get(cast_selection[0]))
    print("DEBUG: Value in relations:", assets.get('relations', {}).get(cast_selection[0]))
