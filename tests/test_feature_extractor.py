from analyzer.app.services.feature_extractor import extract_features
def test_vector_has_36_features():
    r=extract_features([{"output_fields":{"evt.type":"mkdirat"}}])
    assert len(r["feature_vector"])==36
    assert r["feature_counts"]["mkdir"]==1
