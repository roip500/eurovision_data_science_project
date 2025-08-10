import pandas as pd

def merge_datasets():
    # Load datasets
    df2 = pd.read_csv('../datasets/eurovision_dataset_2.csv')
    df1 = pd.read_csv('../datasets/eurovision_dataset_1.csv')

    # Rename df2 for consistency
    df1_renamed = df1.rename(columns={
        'performer': 'artist',
        'to_country': 'country',
        'place_final': 'place',
        'points_final': 'points',
        'running_final': 'running_order'
    })

    # Deduplicate to avoid Cartesian multiplication
    df2 = df2.drop_duplicates(subset=['year', 'country', 'song'])
    df1_renamed = df1_renamed.drop_duplicates(subset=['year', 'country', 'song'])

    # 1️⃣ Inner merge → rows in both datasets
    inner_merge = pd.merge(
        df2, df1_renamed,
        on=['year', 'country', 'song'],
        how='inner',
        suffixes=('', '_drop')
    )

    # 2️⃣ Find rows in df2 that are not in df1
    only_df2 = df2.merge(
        df1_renamed[['year', 'country', 'song']],
        on=['year', 'country', 'song'],
        how='left',
        indicator=True
    ).query('_merge == "left_only"').drop(columns=['_merge'])

    # 3️⃣ Combine the inner merge and the only_df2 table
    merged_tb = pd.concat([inner_merge, only_df2], ignore_index=True)

    # Save to CSV
    # merged_tb.to_csv('datasets/final_merged.csv', index=False)

    print("Inner merge rows:", inner_merge.shape[0])
    print("Only in df2 rows:", only_df2.shape[0])
    print("Final merged rows:", merged_tb.shape[0])

    # Load LGBTQ dataset
    lgbtq_df = pd.read_excel('datasets/lgbtq_eurovision_artists.xlsx')

    # Make sure the column names match for the join
    lgbtq_df = lgbtq_df.rename(columns={
        'Artist': 'artist',
        'Country': 'country',
        'Year': 'year',
        'Song': 'song',
        'Sexual orientation or gender identity': 'artist sexuality'
    })

    # Merge to bring in sexuality info
    merged_with_sexuality = pd.merge(
        merged_tb,
        lgbtq_df[['artist', 'country', 'year', 'artist sexuality']],
        on=['artist', 'country', 'year'],
        how='left'
    )

    # Fill missing sexuality with "straight"
    merged_with_sexuality['artist sexuality'] = merged_with_sexuality['artist sexuality'].fillna('straight')

    # Save final dataset
    merged_with_sexuality.to_csv('datasets/final_merged.csv', index=False)

    print("Added 'artist sexuality' column. Saved to datasets/final_merged_with_sexuality.csv")

if __name__ == '__main__':
    merge_datasets()