declare @fecha_inicio int = 20250801;
declare @fecha_fin int = 20250831;

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
            cli.tel1,
            cli.tel2,
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
            isnull(p.num_productos, 0) as num_productos,
			isnull(pa.productos_activos, 0) as productos_activos
        from dim_cliente cli
        left join (
            select 
				cliente_Skey, 
				count(*) as num_productos
            from (
                    select col.cliente_Skey from fac_colocacion col
                    union all
                    select cap.cliente_Skey from fac_captacion cap
                    union all
                    select trj.cliente_Skey from fac_tarjeta trj
                ) as productos_por_cliente
                group by cliente_Skey
        ) p on p.cliente_Skey = cli.cliente_Skey
		left join (
			select	
				cliente_Skey,
				count(*) as productos_activos
			from (
					select col.cliente_Skey from fac_colocacion col where col.col_estado_Skey not in (25,26,27,28,29,30,31,32,33,34,35,36,45,46,47,48)
                    union all
                    select cap.cliente_Skey from fac_captacion cap where cap.estado_cartera_Skey <> 3
                    union all
                    select trj.cliente_Skey from fac_tarjeta trj where trj.estado <> 3
				) as productos_por_cliente
			group by cliente_Skey
		) pa on pa.cliente_Skey = cli.cliente_Skey
        where cli.cod_cliente = '039000001617'
    ),
    prods_creds as (
        select 
            ic.cliente_Skey,
            ic.cod_cliente,
            ic.nombre,
            col.fac_colocacion_Skey as prod_key,
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
            cap.fac_captacion_skey as prod_key,
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
            trj.tarjeta_skey as prod_key,
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
    prom_capt as (
        select
            smcap.fac_captacion_Skey,
            avg(smcap.cantidad_creditos) as cantidad_creditos,
            avg(smcap.creditos) as creditos,
            avg(smcap.cantidad_debitos) as cantidad_debitos,
            avg(smcap.debitos) as debitos
        from (
            select
                    mov.fac_captacion_Skey,
                    left(cast(mov.fecha_operacion as varchar), 6) as mes,
                    count(case when trx.tipo_movimiento = 'CREDITO' then 1 else null end) as cantidad_creditos,
                    sum(case when trx.tipo_movimiento = 'CREDITO' then mov.valor_operacion else 0 end) as creditos,
                    count(case when trx.tipo_movimiento = 'DEBITO' then 1 else null end) as cantidad_debitos,
                    sum(case when trx.tipo_movimiento = 'DEBITO' then mov.valor_operacion else 0 end) as debitos
                from fac_movimientos mov
                join info_clientes ic on ic.cliente_Skey = mov.cliente_Skey
                join dim_transacciones trx on trx.trx_Skey = mov.trx_Skey and trx.relacion_cuenta = 'RELACIONADA'
                where mov.estado_trx_Skey = 1 and mov.fecha_operacion between @fecha_inicio and @fecha_fin --and cliente_Skey is not null and cliente_Skey <> -1
                group by mov.fac_captacion_Skey, 
                    left(cast(fecha_operacion as varchar), 6)
            ) as smcap
            group by smcap.fac_captacion_Skey
    ),
    prom_trj as (
        select
            smtrj.tarjeta_skey,
            avg(smtrj.cantidad_creditos) as cantidad_creditos,
            -1*avg(smtrj.creditos) as creditos,
            avg(smtrj.cantidad_debitos) as cantidad_debitos,
            avg(smtrj.debitos) as debitos
        from (
            select	
                movt.tarjeta_skey,
                left(cast(movt.fecha_trx as varchar), 6) as mes,
                count(case when movt.monto <> 0 and movt.cod_trx in (2,11,13,15,30,511,513,730,732,848) then 1 else null end) as cantidad_creditos,
                sum(case when movt.monto <> 0 and movt.cod_trx in (2,11,13,15,30,511,513,730,732,848) then movt.monto else null end) as creditos,
                count(case when movt.monto <> 0 and movt.cod_trx not in (2,11,13,15,30,511,513,730,732,848) then 1 else null end) as cantidad_debitos,
                sum(case when movt.monto <> 0 and movt.cod_trx not in (2,11,13,15,30,511,513,730,732,848) then movt.monto else null end) as debitos
            from fac_movimientos_tarjeta movt
            join fac_tarjeta trj on trj.tarjeta_skey = movt.tarjeta_skey
            join info_clientes ic on ic.cliente_Skey = trj.cliente_Skey
            where movt.cod_trx not in (5,8,9,10,19,21,22,29,32,41,50,104,451,453,553,554,637,665,671,689,701,715,717,731,733,747,751,754,821,849,851)
                and movt.fecha_trx between @fecha_inicio and @fecha_fin
            group by movt.tarjeta_skey,
                left(cast(movt.fecha_trx as varchar), 6)
        ) as smtrj
        group by smtrj.tarjeta_skey
    ),
    prom_col as (
        select
            smcol.fac_colocacion_skey,
            null as cantidad_creditos,
            null as creditos, 
            avg(smcol.cantidad_debitos) as cantidad_debitos,
            avg(smcol.debitos) as debitos
        from (
            select
                movc.fac_colocacion_skey,
                left(cast(movc.fecha_trx as varchar), 6) as mes,
                count(case when movc.total <> 0 then 1 else null end) as cantidad_debitos,
                sum(case when movc.total <> 0 then movc.total else null end) as debitos
            from fac_movimientos_colocacion movc
            join fac_colocacion col on col.fac_colocacion_Skey = movc.fac_colocacion_skey
            join info_clientes ic on ic.cliente_Skey = col.cliente_Skey
            where movc.trx_col_skey in (1,3) and movc.fecha_trx between @fecha_inicio and @fecha_fin
            group by movc.fac_colocacion_skey,
                left(cast(movc.fecha_trx as varchar), 6)
        ) as smcol
        group by smcol.fac_colocacion_skey
    ),
    creditos as (
        select 
            pcr.cliente_Skey,
            pcr.cod_cliente,
            pcr.nombre,
            pcr.cod_prod,
            pcr.estado,
            pcr.saldo,
            pcr.deuda,
            pcr.producto,
            pcr.subproducto,
            pco.cantidad_creditos,
            pco.creditos,
            pco.cantidad_debitos,
            pco.debitos,
            pcr.cod_sucursal,
            pcr.sucursal,
            pcr.origen
        from prods_creds pcr 
        left join prom_col pco on pco.fac_colocacion_skey = pcr.prod_key
    ), 
    cuentas as (
        select 
            pcu.cliente_Skey,
            pcu.cod_cliente,
            pcu.nombre,
            pcu.cod_prod,
            pcu.estado,
            pcu.saldo,
            pcu.deuda,
            pcu.producto,
            pcu.subproducto,
            pct.cantidad_creditos,
            pct.creditos,
            pct.cantidad_debitos,
            pct.debitos,
            pcu.cod_sucursal,
            pcu.sucursal,
            pcu.origen
        from prods_cuentas pcu
        left join prom_capt pct on pct.fac_captacion_Skey = pcu.prod_key
    ), 
    tarjeta as (
        select 
            ptr.cliente_Skey,
            ptr.cod_cliente,
            ptr.nombre,
            ptr.cod_prod,
            ptr.estado,
            ptr.saldo,
            ptr.deuda,
            ptr.producto,
            ptr.subproducto,
            ptrj.cantidad_creditos,
            ptrj.creditos,
            ptrj.cantidad_debitos,
            ptrj.debitos,
            ptr.cod_sucursal,
            ptr.sucursal,
            ptr.origen
        from prods_trj ptr 
        left join prom_trj ptrj on ptrj.tarjeta_skey = ptr.prod_key
    ), 
    productos as (
        select * from creditos
        union 
        select * from cuentas
        union 
        select * from tarjeta
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
select * from info_clientes