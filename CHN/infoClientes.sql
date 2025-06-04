with info_clientes as (
        select
            cli.cliente_Skey,
            cli.cod_cliente,
            cli.nombre,
            convert(varchar, cli.fecha_alta, 23) fecha_alta,
            cli.clase,
            cli.pais,
            cli.profesion,
            cli.direccion_cliente,
            cli.estadoCliente,
            cli.fecha_ultima_actualizacion fecha_ultima_actualizacion,
            cli.agencia_ultima_actualizacion,
            cli.cliente_pep,
            cli.cliente_cpe,
            cli.tipoPersona,
            cli.tipo_sociedad,
            cli.sectorEconomico,
            cli.actividad_economica,
            cli.sector_economico_ive,
            cli.nacionalidad,
            cli.lugar_nacimiento_extranjero,
            cli.institucion,
            cli.puesto,
            cli.firmante,
            cli.codigo_empleado,
            cli.direcciones_np,
            cli.nombre_notario,
            cli.cod_representante_legal,
            cli.nombre_representante_legal,
            isnull(p.num_productos, 0) as num_productos
        from dim_cliente cli
        left join (
            select cliente_Skey, count(*) as num_productos
            from (
                    select col.cliente_Skey from fac_colocacion col
                    union all
                    select cap.cliente_Skey from fac_captacion cap
                    union all
                    select trj.cliente_Skey from fac_tarjeta trj
                ) as productos_por_cliente
                group by cliente_Skey
        ) p on p.cliente_Skey = cli.cliente_Skey
        where cli.cod_cliente {cli}
    ),
    prods_creds as (
        select 
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            col.cod_col_cartera as cod_prod,
            ce.nombre as estado,
			col.monto_desembolsado as saldo,
			col.monto_capital_total as deuda,
            prod.descripcion as producto,
            sp.descripcion as subproducto,
            suc.cod_sucursal,
            suc.nombre as sucursal,
            origen = 'COLOCACION (Credito)'
        from fac_colocacion col
        right join info_clientes ic on ic.cliente_Skey = col.cliente_Skey
            --and (col.col_estado_Skey between 25 and 36 or col.col_estado_Skey between 45 and 48)
        join dim_producto prod on prod.producto_SKey = col.producto_SKey
        join dim_subproducto sp on sp.subproducto_SKey = col.subproducto_SKey
        join dim_sucursal suc on suc.sucursal_Skey = col.sucursal_Skey
        join dim_col_estado ce on ce.col_estado_Skey = col.col_estado_Skey
        --where (col.col_estado_Skey between 25 and 36 or col.col_estado_Skey between 45 and 48) -- no cancelados o anulados
    ),
    prods_cuentas as (
        select 
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            cap.cod_cuenta as cod_prod,
            ec.nombre as estado,
			cap.saldo_disponible as saldo,
			NULL as deuda,
            cp.descripcion as producto,
            cs.descripcion as subproducto,
            suc.cod_sucursal,
            suc.nombre as sucursal,
            origen = 'CAPTACION (Cuenta)'
        from fac_captacion cap
        right join info_clientes ic on ic.cliente_Skey = cap.cliente_Skey
            --and cap.estado_cartera_Skey = 2 -- productos activos
        join dim_cap_producto cp on cp.producto_SKey = cap.producto_SKey
        join dim_cap_subproducto cs on cs.subproducto_SKey = cap.subproducto_SKey
        join dim_sucursal suc on suc.sucursal_Skey = cap.sucursal_apertura_skey
        join dim_estado_cartera ec on ec.estado_cartera_SKey = cap.estado_cartera_Skey
        --where cap.estado_cartera_Skey = 2 -- productos activos
    ),
    prods_trj as (
        select 
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            trj.cod_col_cartera as cod_prod,
            ec.nombre as estado,
			trj.limite_credito as saldo,
			trj.monto_capital as deuda,
            producto = 'TARJETA CREDITO',
            tt.nombre as subproducto,
            suc.cod_sucursal,
            suc.nombre as sucursal,
            origen = 'TARJETA (T.C.)'
        from fac_tarjeta as trj
        right join info_clientes ic on ic.cliente_Skey = trj.cliente_Skey
            --and trj.estado = 2 -- activa
        join dim_tipotarjeta tt on tt.tipotarjeta_Skey = trj.tipotarjeta_skey
        join dim_sucursal suc on suc.sucursal_Skey = trj.sucursal_skey
        join dim_estado_cartera ec on ec.estado_cartera_SKey = trj.estado
        --where trj.estado = 2 -- activa
    ),
    productos as (
        select * from prods_creds
        union 
        select * from prods_cuentas
        union 
        select * from prods_trj
    ),
    accionistas as (
        select
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            acc.identificacion_accionista,
            acc.nombre_accionista,
            acc.porcentaje_accionista
        from fac_accionista acc
        join info_clientes ic on ic.cliente_Skey = acc.cliente_skey
    ),
    beneficiarios as (
        select
            pc.cliente_Skey,
            pc.cod_cliente,
            pc.nombre,
            pc.cod_prod,
            pc.estado,
            pc.producto,
            pc.subproducto,
            pc.cod_sucursal,
            pc.sucursal,
            ben.nombre_beneficiario,
            ben.porcentaje_beneficiario
        from fac_beneficiario ben
        join prods_cuentas pc on pc.cod_prod = ben.cod_cuenta
    )