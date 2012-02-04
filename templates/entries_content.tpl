<div id="entries">
{% for entry in entries %}
<div class="entry">
  <header>{{ entry.datetime }}</header>
  <div>{{ entry.body }}</div>
  <footer>
    <ul class="tags">
    {% for tag in entry.tags %}
      <li># {{ tag }}</li>
    {% endfor %}
    </ul>
  </footer>
</div>
{% endfor %}
</div>

<footer>
{% if page_prev is defined %}
  <div id="navL"><a href="{{ page_prev }}">&lt;</a></div>
{% endif %}

{% if page_next is defined %}
  <div id="navR"><a href="{{ page_next }}">&gt;</a></div>
{% endif %}
</footer>
