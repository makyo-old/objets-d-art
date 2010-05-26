<form id="update-cart"><!-- for styling -->
<table>
    <thead>
        <th style="text-align: left">Item/Description</th>
        <th>Quantity</th>
    </thead>
    <tbody>
        {% for item in cart.item_set.all %}
        <tr class="{% cycle 'odd' 'even' %}">
            <td><a href="/store/product/{{ item.product.sku }}/">{{ item.product.name }}</a><br />
                {{ item.product.short_desc }}</td>
            <td width="10%" style="text-align: center">{{ item.quantity }}</td>
        </tr>
        {% endfor %}
    </tbody>
    <tfoot>
        <tr>
            <td colspan="3" style="text-align: right">
            </td>
        </tr>
    </tfoot>
</table>
</form>
