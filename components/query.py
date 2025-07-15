# query.py
# -----------------
# Aquí se aloja la consulta SQL optimizada (o vista) para el inventario

INVENTORY_SQL = """
WITH
-- 1) Agrego en InvPorTienda sólo filas con Existencia >= 0 y pre-agrego por Inventario+Tienda
InvPorTienda AS (
  SELECT
    di.Referencia,
    di.CodigoMarca,
    CONCAT(di.Referencia, di.CodigoMarca) AS concatenado,
    di.NombreMarca,
    di.Nombre,
    di.Fabricante,
    dc.NombreSubLinea,
    di.NombreCategoria,
    dt.dimID_Tienda,
    dt.Nombre AS NombreTienda,
    CASE 
      WHEN dt.dimID_Tienda = 2003 THEN 'Valencia Casa Matriz'
      WHEN dt.dimID_Tienda = 2005 THEN 'Oriente - Casa Matriz'
      WHEN dt.dimID_Tienda = 2004 THEN 'Occidente - Casa Matriz'
      WHEN dt.dimID_Tienda = 2006 THEN 'Margarita - Casa Matriz'
      WHEN dt.dimID_Tienda IN (1,1002,1004,1006,1009,1010,1011,1012,
                               1013,1014,1017,1018,1019,1020,1021,1022,
                               1023,1024) THEN 'Oriente - Sucursales'
      WHEN dt.dimID_Tienda IN (1026,1027,1028,1029,1030,1031,1037,1038,
                               1039,1040,1041,1042,1043,1044,1045,1046,
                               1047,1048,1050,1052,1053,1055,2007) THEN 'Occidente - Sucursales'
      WHEN dt.dimID_Tienda IN (1032,1033,1034,1035,1036) THEN 'Margarita - Sucursales'
      ELSE 'Sin region'
    END AS Region,
    SUM(hi.Existencia) AS Existencia,
    MAX(hi.PrecioDetal) AS PrecioDetal,
    MAX(hi.PrecioPromocion) AS PrecioPromocion
  FROM tbDimInventario di
  JOIN tbHecInventario hi
    ON di.dimID_Inventario = hi.dimid_inventario
       AND hi.Existencia >= 0
  JOIN tbDimTiendas dt
    ON hi.dimid_tienda = dt.dimID_Tienda
  JOIN tbDimCategorias dc
    ON di.dimID_Categoria = dc.dimID_Categoria
  GROUP BY
    di.Referencia,
    di.CodigoMarca,
    di.NombreMarca,
    di.Nombre,
    di.Fabricante,
    dc.NombreSubLinea,
    di.NombreCategoria,
    dt.dimID_Tienda,
    dt.Nombre
),
ReferenciasConPositivo AS (
  SELECT
    Referencia,
    CodigoMarca
  FROM InvPorTienda
  WHERE Existencia > 0
  GROUP BY Referencia, CodigoMarca
)

SELECT
  d.concatenado,
  d.Referencia,
  d.NombreMarca,
  d.CodigoMarca,
  d.Nombre,
  d.Fabricante,
  d.NombreSubLinea,
  d.NombreCategoria,
  CONCAT(CAST(ROUND((1.0 - (d.PrecioPromocion/NULLIF(d.PrecioDetal,0))) * 100, 0) AS INT), '%') AS PorcentajeDescuento,
  d.Region,
  d.NombreTienda,
  d.Existencia AS Existencia_Por_Tienda,
  SUM(CASE WHEN d.Region LIKE '%Casa Matriz' THEN d.Existencia ELSE 0 END) OVER (PARTITION BY d.Referencia, d.CodigoMarca) AS Existencia_CasaMatriz,
  SUM(CASE WHEN d.Region LIKE '%Sucursales' THEN d.Existencia ELSE 0 END) OVER (PARTITION BY d.Referencia, d.CodigoMarca) AS Existencia_Sucursales
FROM InvPorTienda d
INNER JOIN ReferenciasConPositivo p
  ON p.Referencia = d.Referencia AND p.CodigoMarca = d.CodigoMarca
ORDER BY d.Referencia;

"""

