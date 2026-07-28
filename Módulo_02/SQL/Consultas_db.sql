use db_jardineria

SELECT 
    c.nombre_cliente,
    p.codigo_pedido,
    p.fecha_pedido
FROM cliente c
INNER JOIN pedido p
ON c.codigo_cliente = p.codigo_cliente;


SELECT 
    c.nombre_cliente,
    p.codigo_pedido,
    pr.nombre AS producto,
    dp.cantidad
FROM cliente c
INNER JOIN pedido p ON c.codigo_cliente = p.codigo_cliente
INNER JOIN detalle_pedido dp ON p.codigo_pedido = dp.codigo_pedido
INNER JOIN producto pr ON dp.codigo_producto = pr.codigo_producto;

SELECT 
    c.nombre_cliente,
    p.codigo_pedido
FROM cliente c
LEFT JOIN pedido p
ON c.codigo_cliente = p.codigo_cliente;

SELECT c.nombre_cliente
FROM cliente c
LEFT JOIN pedido p 
ON c.codigo_cliente = p.codigo_cliente
WHERE p.codigo_pedido IS NULL;

SELECT 
    c.nombre_cliente,
    p.codigo_pedido
FROM cliente c
RIGHT JOIN pedido p
ON c.codigo_cliente = p.codigo_cliente;

SELECT 
    p.codigo_pedido,
    pr.nombre,
    dp.cantidad
FROM producto pr
RIGHT JOIN detalle_pedido dp 
ON pr.codigo_producto = dp.codigo_producto
RIGHT JOIN pedido p 
ON dp.codigo_pedido = p.codigo_pedido;