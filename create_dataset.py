from create_data_set_code import extract_song_db_2, extract_song_db_1, lgtbq_artist_list, merge_datasets


def create_dataset():
    extract_song_db_1.main()  # mute this command if dataset1 exists - takes long
    extract_song_db_2.main()
    lgtbq_artist_list.main()
    merge_datasets.merge_datasets()


if __name__ == '__main__':
    create_dataset()
