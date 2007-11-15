<?python
    from bandradar.widgets import top_venues
?>

<span xmlns:py="http://purl.org/kid/ns#" class="topartists">
    <p py:for="venue in top_venues.get_list()">
        <a href="/venues/${venue['id']}">${venue['name']}</a>
    </p>
</span>

