#!/bin/bash

# Create a copy of the database
DB="${1%.db}-normalized.db"
echo "Copying databse to" $DB
cp $1 $DB
ls -lh $DB

# Extract user info
echo "Creating 'user' table and extracting info"
sqlite-utils extract $DB listens \
    user_id \
    --table users \
    --fk-column user_id \
    --rename user_id name
ls -lh $DB

# Extract artist info
echo "Creating 'artist' table and extracting info"
sqlite-utils extract $DB listens \
    artist_name artist_id \
    --table artists \
    --fk-column artist_id \
    --rename artist_name name \
    --rename artist_id mbid
ls -lh $DB

# Create a new column for album_artist_id in the listens table
echo "Creating 'album_artist_id' column"
sqlite-utils add-column $DB listens album_artist_id
ls -lh $DB

# Run python script to handle album_artist_names
echo "Running python script to handle album artists"
SCRIPT="$(dirname "$0")/handle_album_artists.py"
$SCRIPT $DB
ls -lh $DB

# Remove album_artist_names
echo "Removing album_artist_name column"
sqlite-utils transform --drop album_artist_name $DB listens
ls -lh $DB

# Extract album info
echo "Creating 'album' table and extracting info"
sqlite-utils extract $DB listens \
    album_name album_id album_artist_id \
    --table albums \
    --fk-column album_id \
    --rename album_name title \
    --rename album_id mbid \
    --rename album_artist_id artist_id
ls -lh $DB

# Extract track info
echo "Creating 'track' table and extracting info"
sqlite-utils extract $DB listens \
    artist_id track_id track_name album_id length tracknumber \
    --table tracks \
    --fk-column track_id \
    --rename track_name title \
    --rename track_id mbid
ls -lh $DB

# Re-create foreign key constraints
echo "Creating foreign key constraints between tables"
sqlite-utils add-foreign-key $DB tracks artist_id artists id
sqlite-utils add-foreign-key $DB tracks album_id albums id
sqlite-utils add-foreign-key $DB albums artist_id artists id
sqlite-utils index-foreign-keys $DB
ls -lh $DB
