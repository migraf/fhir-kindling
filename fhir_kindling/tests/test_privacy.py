import pandas as pd

from fhir_kindling.privacy.k_anonymity import is_k_anonymized


def test_k_anonymity(fhir_server):
    test_data = []
    for i in range(100):
        if i % 4 == 0:
            test_data.append({"name": "John", "age": i % 4})
        elif i % 4 == 1:
            test_data.append({"name": "Jack", "age": i % 4})
        elif i % 4 == 2:
            test_data.append({"name": "Jones", "age": i % 4})
        elif i % 4 == 3:
            test_data.append({"name": "Jill", "age": i % 4})

    df = pd.DataFrame(test_data)

    assert is_k_anonymized(df, k=3)

    non_anon_df = df.copy()
    non_anon_df["age"] = list(range(100))
    assert not is_k_anonymized(non_anon_df, k=3)

    assert is_k_anonymized(non_anon_df, k=3, excluded_cols=["age"])

    assert is_k_anonymized(non_anon_df, k=3, id_cols=["name"])


# def test_anonymize(fhir_server):
#     patients = fhir_server.query("Patient").limit(1000).resources
#
#     print(len(patients))
#     df = flatten_resources(patients)
#     anonymize(df)
