<?python
    from bandradar.widgets import top_artists
?>

<span xmlns:py="http://purl.org/kid/ns#" class="topartists">
    <p py:for="artist in top_artists.get_list()">
        <a href="/artists/${artist['quoted_name']}">${artist['name']}</a>
    </p>
</span>

