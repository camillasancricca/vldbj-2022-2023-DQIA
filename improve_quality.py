import random as rd
#queste funzioni sono fatte per non interferire nella modifica di altri errori di qualità contemporaneamente, se si vogliono usare generali bisogna togliere i controlli sulle sovrapposizioni

# imputing missing values

def imputing_missing_values(dataset):

    for col in dataset.columns:
        if (dataset[col].dtype != "object"):
            dataset[col] = dataset[col].fillna(dataset[col].mean())
        else:
            dataset[col] = dataset[col].fillna(dataset[col].mode()[0])

    return dataset

# drop missing values

def drop_missing_values(dataset):
    dataset = dataset.dropna(axis=0, how='any')
    return dataset

# outlier correction

def outlier_correction(dataset, outlier_range, targeted_class):

    for col in dataset.columns:
        if col != targeted_class:
            index = dataset.columns.get_loc(col)
            if (dataset[col].dtype != "object"):
                if ((dataset[col].mean() < outlier_range[index][0]) | (dataset[col].mean() > outlier_range[index][1])):
                    dataset.loc[((dataset[col] < outlier_range[index][0]) | (dataset[col] > outlier_range[index][1])) & dataset[col].notnull(),col]=rd.uniform(outlier_range[index][0],outlier_range[index][1])
                else:
                    dataset.loc[((dataset[col] < outlier_range[index][0]) | (dataset[col] > outlier_range[index][1])) & dataset[col].notnull(),col]=dataset[col].mean()
            else:
                dataset.loc[~dataset[col].isin(outlier_range[index]) & dataset[col].notnull(),col]=dataset[col].mode()[0]

    return dataset

#correct functional dependencies

def correct_incorrect_depedences(dataset, rules, targeted_class, mask):

    columns = dataset.columns
    for r in rules:
        targeted_rows = dataset

        for lhs in r.lhs:
            targeted_rows = targeted_rows.loc[targeted_rows[columns[lhs[1]]] == lhs[0]] #seleziono le lhs (valore a destra della fd)

        for rhs in r.rhs:
            if dataset.columns[rhs[1]] != targeted_class:
                indexes = targeted_rows.index.tolist()
                for i in indexes:
                    OK = True
                    if dataset.columns[rhs[1]] != targeted_class:
                        if mask[targeted_rows.columns.get_loc(columns[rhs[1]])][i] == 2:

                            for lhs in r.lhs:
                                if dataset.columns[lhs[1]] != targeted_class:
                                    if mask[targeted_rows.columns.get_loc(columns[lhs[1]])][i] == 2:
                                        OK = False

                            if (OK):
                                if dataset[columns[rhs[1]]].dtype != "object":
                                    dataset.loc[i:i,columns[rhs[1]]] = float(rhs[0])
                                else:
                                    dataset.loc[i:i,columns[rhs[1]]] = rhs[0]

    return dataset

#substutite the errors with the true value

def true_value_substitution(mask, cleaned_dataset, dataset, dimension):
    N = 0
    if (dimension == "accuracy"):
        N = 3
    if (dimension == "completeness"):
        N = 1
    if (dimension == "consistency"):
        N = 2
    for col in dataset.columns:
        index_no = dataset.columns.get_loc(col)
        to_substitute = cleaned_dataset.loc[mask[index_no] == N,col]
        dataset.loc[mask[index_no] == N,col]=to_substitute
    return dataset