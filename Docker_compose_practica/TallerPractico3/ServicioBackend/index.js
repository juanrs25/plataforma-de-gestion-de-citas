import express from 'express'
import { createPool } from 'mysql2/promise'

const app = express()

const pool = createPool({
    host: 'bd_proyectonotas',
    user: 'root',
    password: "",
    database: 'sistemaNotasBd',
    port: 3306
})

app.get('/', (req, res) => {
    res.send('Servicio BackendFuncionando')
})

app.get('/pruebaconexion', async (req, res) => {
    try {
        await pool.query('SELECT 1')
        res.send('Conectado a la base de datos exitosamente.')
    } catch (error) {
        console.error("Error en la conexión:", error)
        res.status(500).send('Error al conectar con la base de datos.')
    }
})

app.listen(3000)
console.log('Server corriendo en el puerto', 3000)