<div id="index">
  <ul>
{% for page in pages %}
    <li><a href="{{ page.name }}.html">{{ page.name }}</a></li>
{% endfor %}
  </ul>
</div>
