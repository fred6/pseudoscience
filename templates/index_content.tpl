<div id="index">
  <ul>
{% for chunk in chunks %}
    <li><a href="{{ chunk.name }}.html">{{ chunk.name }}</a></li>
{% endfor %}
  </ul>
</div>
