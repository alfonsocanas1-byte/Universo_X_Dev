# --- PANEL F5CO (GESTIÓN TOTAL) ---
elif st.session_state.modulo_activo == "F5CO":
    st.title("🏦 F5CO - Control Central de Usuarios")
    if st.button("⬅️ VOLVER AL INICIO"):
        st.session_state.modulo_activo = "Lobby"
        st.session_state.autenticado = False
        st.rerun()
    
    db = cargar_usuarios()
    tab1, tab2, tab3, tab4 = st.tabs(["💰 CARGAR ABONO", "📊 MOVIMIENTOS", "✏️ EDITAR POR CELULAR", "🗑️ ELIMINAR USUARIOS"])
    
    with tab1: # Carga de Saldo
        tid = st.text_input("Celular Beneficiario")
        amt = st.number_input("Monto Recibido ($)", min_value=0, step=1000)
        if st.button("APLICAR ABONO"):
            if tid in db:
                db[tid]["saldo"] += amt
                db[tid]["movimientos"].append({"tipo": "Abono Efectivo", "monto": amt, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")})
                guardar_usuarios(db); st.success("Abono cargado."); st.rerun()
            else: st.error("Usuario no encontrado.")

    with tab2: # Consulta de Movimientos
        sid = st.text_input("Consultar Celular")
        if sid in db:
            st.write(f"### Estado de Cuenta: {db[sid].get('nombre_completo', 'N/A')}")
            st.metric("Saldo Actual", f"${db[sid].get('saldo', 0.0):,}")
            df_movs = pd.DataFrame(db[sid].get("movimientos", []))
            if not df_movs.empty: st.table(df_movs.iloc[::-1])

    with tab3: # EDITAR SOLO (Digitar Celular)
        st.subheader("Edición de Precisión")
        cel_editar = st.text_input("Digite el número de celular literal para editar")
        
        if cel_editar in db:
            u_data = db[cel_editar]
            st.info(f"Editando: {u_data.get('nombre_completo')} | Cuenta: {u_data.get('cuenta_f5co')}")
            with st.form("precision_edit"):
                col1, col2 = st.columns(2)
                n_nom = col1.text_input("Nombre Completo", value=u_data.get('nombre_completo', ''))
                n_usr = col2.text_input("Username", value=u_data.get('username', ''))
                n_clave = col1.text_input("Clave Secreta", value=u_data.get('clave', ''))
                n_saldo = col2.number_input("Saldo Manual", value=float(u_data.get('saldo', 0.0)))
                n_ind = col1.text_input("Indicio Clave", value=u_data.get('indicio', ''))
                n_res = col2.text_input("Respuesta Secreta", value=u_data.get('respuesta_secreta', ''))
                
                if st.form_submit_button("💾 ACTUALIZAR DATOS"):
                    db[cel_editar].update({
                        "nombre_completo": n_nom, "username": n_usr,
                        "clave": n_clave, "saldo": n_saldo,
                        "indicio": n_ind, "respuesta_secreta": n_res
                    })
                    guardar_usuarios(db)
                    st.success("Cambios guardados en usuarios_x.json")
        elif cel_editar:
            st.warning("El celular digitado no existe en la base de datos.")

    with tab4: # ELIMINAR SOLO (Desplegar Lista)
        st.subheader("Zona de Eliminación (Cuidado)")
        if st.checkbox("🔓 Desplegar todos los usuarios para eliminación"):
            for celular, info in db.items():
                col_u, col_b = st.columns([0.8, 0.2])
                col_u.write(f"**ID:** {celular} | **Nombre:** {info.get('nombre_completo')} | **Saldo:** ${info.get('saldo'):,}")
                if col_b.button("🗑️ ELIMINAR", key=f"del_{celular}"):
                    # No puedes borrarte a ti mismo si estás logueado administrativamente
                    if celular == st.session_state.get('user_id'):
                        st.error("No puedes eliminar tu propia cuenta mientras estás en uso.")
                    else:
                        del db[celular]
                        guardar_usuarios(db)
                        st.success(f"Usuario {celular} borrado del Universo X.")
                        st.rerun()