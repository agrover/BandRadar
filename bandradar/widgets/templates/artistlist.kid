<?python
    from bandradar.widgets import artistlist
?>

<span xmlns:py="http://purl.org/kid/ns#" class="artistlist">
    ${XML(artistlist.get_list(event))}
</span>
