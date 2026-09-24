USE Farmacia_BD;
GO

USE Farmacia_BD;
GO

SELECT * FROM Clientes;

SELECT * FROM Medicamentos;

SELECT * FROM Sucursales;

SELECT * FROM Ventas;

SELECT 'Clientes' AS Tabla, COUNT(*) AS Total_Registros FROM Clientes
UNION ALL
SELECT 'Medicamentos', COUNT(*) FROM Medicamentos
UNION ALL
SELECT 'Sucursales', COUNT(*) FROM Sucursales
UNION ALL
SELECT 'Ventas', COUNT(*) FROM Ventas;