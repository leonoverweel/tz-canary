import pandas as pd


def generate_example_data():
    df_example = pd.DataFrame(
        index=pd.date_range(
            start="2023-01-01",
            end="2023-12-31",
            freq="15T",
            tz="Europe/Amsterdam",
            name="datetime",
        ),
        data={"best_color": "orange"},
    )

    # We strip the time zone information from the index to simulate a file that does not
    #   specify time zone information.
    df_example.index = df_example.index.tz_localize(None)

    df_example.to_csv("example_data.csv")


if __name__ == "__main__":
    generate_example_data()
