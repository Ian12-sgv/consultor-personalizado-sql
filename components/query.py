# query.py
# -----------------
# Aquí se aloja la consulta SQL optimizada (o vista) para el inventario

INVENTORY_SQL = """
WITH InvPorTienda AS (
  SELECT
    di.Referencia,
    di.CodigoMarca,
    di.CodigoBarra AS CodigoBarra,
    CONCAT(di.Referencia, di.CodigoMarca) AS Concatenar,
    di.NombreMarca,
    di.Nombre,
    di.Fabricante,
	dc.CodigoSubLinea,
    dc.NombreSubLinea,
    dc.Nombre AS NombreCategoriaPrincipal,
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
    MAX(hi.PrecioPromocion) AS PrecioPromocion,
    hi.Promocion AS Promocion,
    hi.Status AS Status
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
    di.CodigoBarra,
    di.NombreMarca,
    di.Nombre,
    di.Fabricante,
	dc.CodigoSubLinea,
    dc.NombreSubLinea,
    dc.Nombre,
    di.NombreCategoria,
    dt.dimID_Tienda,
    dt.Nombre,
    hi.Promocion,
    hi.Status
),
ReferenciasConPositivo AS (
  SELECT
    Referencia,
    CodigoMarca
  FROM InvPorTienda
  WHERE Existencia > 0
  GROUP BY Referencia, CodigoMarca
),
Consulta1 AS (
  SELECT
    d.Concatenar,
    d.Referencia,
    d.CodigoBarra,
    d.NombreMarca,
    d.CodigoMarca,
    d.Nombre,
    d.Fabricante,
	d.CodigoSubLinea,
    d.NombreSubLinea AS Linea,
    d.NombreCategoriaPrincipal,
    d.NombreCategoria,
    CASE 
      WHEN d.PrecioPromocion = 0 THEN '0%'
      WHEN d.PrecioDetal = 0 THEN '0%'
      WHEN d.PrecioPromocion = d.PrecioDetal THEN '0%'
      ELSE CONCAT(
        CAST(ROUND((1.0 - (d.PrecioPromocion/NULLIF(d.PrecioDetal,0))) * 100, 0) AS INT),
        '%'
      )
    END AS Descuento,
    CASE 
      WHEN d.NombreSubLinea IN (
        'PANTYS','BRASSIER','BOXER / INTERIOR','PIJAMA','PIJAMAS',
        'ROPA EXTERIOR','ROPA DEPORTIVA','ROPA DE PLAYA','LENCERIA',
        'FAJAS','CALCETERÍA','ARTICULOS DE SERVICIO','ACCESORIOS'
      ) THEN 'Raul'
      WHEN d.NombreSubLinea IN (
        'COSM TICOS','BISUTERIA - JOYERIA','HIGIENE - CUIDADO PERSONAL',
        'MAQUILLAJE','BISUTERIA- CABELLO','U AS','BOLSAS DE REGALO'
      ) THEN 'Jesenia'
      WHEN d.NombreSubLinea IN (
        'CALZADOS','BOLSOS','HOGAR','TEXTILES HOGAR','GORRAS / PASAMONTA AS0',
        'LENTES','ESCOLAR','PAPELERIA ESCOLAR','BALONES'
      ) THEN 'Dairo'
      ELSE 'Sin encargado'
    END AS Encargado,
    d.Region,
    d.NombreTienda,
    d.Existencia AS Existencia_Total,
    d.Promocion,
    d.Status,
    SUM(
      CASE WHEN d.Region LIKE '%Casa Matriz' THEN d.Existencia ELSE 0 END
    ) OVER (
      PARTITION BY d.Referencia, d.CodigoMarca
    ) AS Existencia_Total_CasaMatriz,
    SUM(
      CASE WHEN d.Region LIKE '%Sucursales' THEN d.Existencia ELSE 0 END
    ) OVER (
      PARTITION BY d.Referencia, d.CodigoMarca
    ) AS Existencia_Total_Sucursales
  FROM InvPorTienda d
  JOIN ReferenciasConPositivo p
    ON p.Referencia = d.Referencia
   AND p.CodigoMarca = d.CodigoMarca
),
UltimoMovimiento AS (
  SELECT
    CONCAT(I.Referencia, I.CodigoMarca) AS Concatenar,
    I.CodigoBarra,
    I.Referencia,
    I.CodigoMarca,
    M.Nombre AS Marca,
    I.Nombre,
    F.Nombre AS Fabricante,
    LEFT(C.Codigo, 4) AS CategoriaCodigo,
    C.Nombre AS CategoriaNombre,
    CC.Nombre AS Linea,
    MT.Cantidad AS Cantidad,
    T.Correccion,
    MT.Numero AS NumeroTransferencia,
    CONVERT(VARCHAR, T.Fecha, 103) AS Fecha,
    T.Observacion,
    ROW_NUMBER() OVER (
      PARTITION BY I.Referencia, I.CodigoMarca 
      ORDER BY T.Fecha DESC, MT.Numero DESC
    ) AS RN
  FROM [J101010100_999911].[dbo].[MOVTRANSFERENCIAS] MT
  RIGHT JOIN [J101010100_999911].[dbo].[INVENTARIO] I ON I.CodigoBarra = MT.CodigoBarra
  RIGHT JOIN [J101010100_999911].[dbo].[CATEGORIAS] C ON I.Categoria = C.Codigo
  LEFT JOIN [J101010100_999911].[dbo].[MARCAS] M ON I.CodigoMarca = M.Codigo
  LEFT JOIN [J101010100_999911].[dbo].[CATEGORIAS] CC ON LEFT(C.Codigo, 4) = CC.Codigo
  INNER JOIN [J101010100_999911].[dbo].[TRANSFERENCIAS] T ON T.Numero = MT.Numero
  INNER JOIN [J101010100_999911].[dbo].[SUCURSALES] S ON S.Codigo = T.CodigoRecibe
  INNER JOIN [J101010100_999911].[dbo].[FABRICANTES] F ON F.Codigo = I.Fabricante
  WHERE T.Fecha BETWEEN '20240101' AND GETDATE()
    --AND T.CodigoRecibe IN ('999999')
    AND T.Status IN ('2')
    AND MT.Cantidad NOT IN ('1', '-1')
    --AND (
      --T.Observacion NOT LIKE '%MG%'
      --AND T.Observacion NOT LIKE '%Margarita%'
      --AND T.Observacion NOT LIKE '%Mgta%'
      --AND T.Observacion NOT LIKE '%organza%'
    --)
)
SELECT
  c1.Concatenar,
  c1.Referencia,
  c1.CodigoBarra,
  c1.NombreMarca,
  c1.CodigoMarca,
  c1.Nombre,
  c1.Fabricante,
  c1.CodigoSubLinea,
  c1.Linea,
  c1.NombreCategoriaPrincipal,
  c1.NombreCategoria,
  c1.Descuento,
  c1.Encargado,
  c1.Region,
  c1.NombreTienda,
  c1.Existencia_Total,
  c1.Promocion,
  c1.Status,
  c1.Existencia_Total_CasaMatriz,
  c1.Existencia_Total_Sucursales,
  c2.Fecha
FROM Consulta1 c1
INNER JOIN UltimoMovimiento c2
  ON c1.Concatenar = c2.Concatenar
WHERE c2.RN = 1
ORDER BY c1.Referencia;



"""

