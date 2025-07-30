import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Textarea } from './components/ui/textarea';
import { Badge } from './components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from './components/ui/sheet';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Checkbox } from './components/ui/checkbox';
import { 
  Package, 
  Users, 
  FileText, 
  Truck, 
  CheckCircle, 
  LogOut, 
  Plus,
  Settings,
  Search,
  Filter,
  Download
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Equipment types
const EQUIPMENT_TYPES = [
  'Espaldera',
  'Mascara', 
  'Regulador',
  'Detector Portátil de Gas',
  'SLS',
  'Module Control'
];

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [currentModule, setCurrentModule] = useState('entrada');
  
  // States for data
  const [clients, setClients] = useState([]);
  const [equipment, setEquipment] = useState([]);
  const [manufacturers, setManufacturers] = useState([]);
  const [models, setModels] = useState([]);
  const [faultTypes, setFaultTypes] = useState([]);
  const [purchaseOrders, setPurchaseOrders] = useState([]);

  // Form states
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [equipmentForm, setEquipmentForm] = useState({
    orden_trabajo: '',
    cliente_id: '',
    cliente_nombre: '',
    tipo_equipo: '',
    modelo: '',
    ato: '',
    fabricante: '',
    numero_serie: '',
    fecha_fabricacion: '',
    tipo_fallo: '',
    observaciones: '',
    numero_serie_sensor: '',
    fecha_instalacion_sensor: ''
  });

  const [clientForm, setClientForm] = useState({
    nombre: '',
    cif: '',
    telefono: '',
    email: ''
  });

  const [showClientDialog, setShowClientDialog] = useState(false);
  const [showNewManufacturer, setShowNewManufacturer] = useState(false);
  const [showNewModel, setShowNewModel] = useState(false);
  const [newManufacturer, setNewManufacturer] = useState('');
  const [newModel, setNewModel] = useState('');

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      setIsLoggedIn(true);
      fetchUserData(savedToken);
      loadInitialData(savedToken);
    }
  }, []);

  const fetchUserData = async (authToken) => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user data:', error);
      logout();
    }
  };

  const loadInitialData = async (authToken) => {
    try {
      const headers = { Authorization: `Bearer ${authToken}` };
      
      const [clientsRes, equipmentRes, manufacturersRes, modelsRes, faultTypesRes, purchaseOrdersRes] = await Promise.all([
        axios.get(`${API}/clientes`, { headers }),
        axios.get(`${API}/equipos`, { headers }),
        axios.get(`${API}/fabricantes`, { headers }),
        axios.get(`${API}/modelos`, { headers }),
        axios.get(`${API}/tipos-fallo`, { headers }),
        axios.get(`${API}/ordenes-compra`, { headers })
      ]);

      setClients(clientsRes.data);
      setEquipment(equipmentRes.data);
      setManufacturers(manufacturersRes.data);
      setModels(modelsRes.data);
      setFaultTypes(faultTypesRes.data);
      setPurchaseOrders(purchaseOrdersRes.data);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const login = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/auth/login`, loginForm);
      const authToken = response.data.access_token;
      setToken(authToken);
      setIsLoggedIn(true);
      localStorage.setItem('token', authToken);
      fetchUserData(authToken);
      loadInitialData(authToken);
    } catch (error) {
      alert('Usuario o contraseña incorrectos');
    }
  };

  const logout = () => {
    setIsLoggedIn(false);
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const createClient = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/clientes`, clientForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setClients([...clients, response.data]);
      setClientForm({ nombre: '', cif: '', telefono: '', email: '' });
      setShowClientDialog(false);
    } catch (error) {
      console.error('Error creating client:', error);
    }
  };

  const createEquipment = async (e) => {
    e.preventDefault();
    try {
      const formData = { ...equipmentForm };
      if (formData.fecha_fabricacion) {
        formData.fecha_fabricacion = new Date(formData.fecha_fabricacion).toISOString();
      }
      if (formData.fecha_instalacion_sensor) {
        formData.fecha_instalacion_sensor = new Date(formData.fecha_instalacion_sensor).toISOString();
      }
      
      const response = await axios.post(`${API}/equipos`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setEquipment([...equipment, response.data]);
      setEquipmentForm({
        orden_trabajo: '',
        cliente_id: '',
        cliente_nombre: '',
        tipo_equipo: '',
        modelo: '',
        ato: '',
        fabricante: '',
        numero_serie: '',
        fecha_fabricacion: '',
        tipo_fallo: '',
        observaciones: '',
        numero_serie_sensor: '',
        fecha_instalacion_sensor: ''
      });
      
      alert('Equipo registrado correctamente');
    } catch (error) {
      console.error('Error creating equipment:', error);
      alert('Error al registrar el equipo');
    }
  };

  const addManufacturer = async () => {
    if (!newManufacturer.trim()) return;
    try {
      const response = await axios.post(`${API}/fabricantes?name=${encodeURIComponent(newManufacturer)}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setManufacturers([...manufacturers, response.data]);
      setNewManufacturer('');
      setShowNewManufacturer(false);
    } catch (error) {
      console.error('Error adding manufacturer:', error);
    }
  };

  const addModel = async () => {
    if (!newModel.trim() || !equipmentForm.tipo_equipo) return;
    try {
      const response = await axios.post(`${API}/modelos?name=${encodeURIComponent(newModel)}&equipment_type=${encodeURIComponent(equipmentForm.tipo_equipo)}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setModels([...models, response.data]);
      setNewModel('');
      setShowNewModel(false);
    } catch (error) {
      console.error('Error adding model:', error);
    }
  };

  const handleClientSelect = (clientId) => {
    const selectedClient = clients.find(c => c.id === clientId);
    if (selectedClient) {
      setEquipmentForm({
        ...equipmentForm,
        cliente_id: clientId,
        cliente_nombre: selectedClient.nombre
      });
    }
  };

  const requiresSensorInfo = () => {
    const selectedFaultType = faultTypes.find(ft => ft.nombre === equipmentForm.tipo_fallo);
    return selectedFaultType?.requiere_sensor && equipmentForm.tipo_equipo === 'Detector Portátil de Gas';
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-slate-800">
              Gestor Envíos a Fábrica
            </CardTitle>
            <p className="text-slate-600">ASCONSAr</p>
          </CardHeader>
          <CardContent>
            <form onSubmit={login} className="space-y-4">
              <div>
                <Label htmlFor="username">Usuario</Label>
                <Input
                  id="username"
                  type="text"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label htmlFor="password">Contraseña</Label>
                <Input
                  id="password"
                  type="password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                Iniciar Sesión
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-800">
            Gestor Envíos a Fábrica - ASCONSAr
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-slate-600">Bienvenido, {user?.username}</span>
            <Button variant="outline" onClick={logout}>
              <LogOut className="h-4 w-4 mr-2" />
              Cerrar Sesión
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white h-screen shadow-sm">
          <nav className="p-4 space-y-2">
            <Button
              variant={currentModule === 'entrada' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentModule('entrada')}
            >
              <Package className="h-4 w-4 mr-2" />
              Entrada de Equipos
            </Button>
            <Button
              variant={currentModule === 'gestion' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentModule('gestion')}
            >
              <FileText className="h-4 w-4 mr-2" />
              Gestión Administrativa
            </Button>
            <Button
              variant={currentModule === 'respuesta' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentModule('respuesta')}
            >
              <Truck className="h-4 w-4 mr-2" />
              Respuesta Fabricante
            </Button>
            <Button
              variant={currentModule === 'recepcion' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentModule('recepcion')}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Recepción ASCONSA
            </Button>
            <Button
              variant={currentModule === 'completados' ? 'default' : 'ghost'}
              className="w-full justify-start"
              onClick={() => setCurrentModule('completados')}
            >
              <Settings className="h-4 w-4 mr-2" />
              Envíos Completados
            </Button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {currentModule === 'entrada' && (
            <div className="max-w-4xl mx-auto">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-slate-800">Entrada de Equipos</h2>
                <Dialog open={showClientDialog} onOpenChange={setShowClientDialog}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="h-4 w-4 mr-2" />
                      Nuevo Cliente
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Agregar Nuevo Cliente</DialogTitle>
                    </DialogHeader>
                    <form onSubmit={createClient} className="space-y-4">
                      <div>
                        <Label>Nombre</Label>
                        <Input
                          value={clientForm.nombre}
                          onChange={(e) => setClientForm({...clientForm, nombre: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label>CIF</Label>
                        <Input
                          value={clientForm.cif}
                          onChange={(e) => setClientForm({...clientForm, cif: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label>Teléfono</Label>
                        <Input
                          value={clientForm.telefono}
                          onChange={(e) => setClientForm({...clientForm, telefono: e.target.value})}
                          required
                        />
                      </div>
                      <div>
                        <Label>Email (opcional)</Label>
                        <Input
                          type="email"
                          value={clientForm.email}
                          onChange={(e) => setClientForm({...clientForm, email: e.target.value})}
                        />
                      </div>
                      <Button type="submit">Guardar Cliente</Button>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Registrar Nuevo Equipo</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={createEquipment} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label>Orden de Trabajo</Label>
                      <Input
                        value={equipmentForm.orden_trabajo}
                        onChange={(e) => setEquipmentForm({...equipmentForm, orden_trabajo: e.target.value})}
                        required
                      />
                    </div>

                    <div>
                      <Label>Cliente</Label>
                      <Select onValueChange={handleClientSelect}>
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar cliente" />
                        </SelectTrigger>
                        <SelectContent>
                          {clients.map((client) => (
                            <SelectItem key={client.id} value={client.id}>
                              {client.nombre} - {client.cif}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Tipo de Equipo</Label>
                      <Select onValueChange={(value) => setEquipmentForm({...equipmentForm, tipo_equipo: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar tipo" />
                        </SelectTrigger>
                        <SelectContent>
                          {EQUIPMENT_TYPES.map((type) => (
                            <SelectItem key={type} value={type}>
                              {type}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <Label>Modelo</Label>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowNewModel(true)}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                      <Select onValueChange={(value) => setEquipmentForm({...equipmentForm, modelo: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar modelo" />
                        </SelectTrigger>
                        <SelectContent>
                          {models
                            .filter(model => model.tipo_equipo === equipmentForm.tipo_equipo)
                            .map((model) => (
                              <SelectItem key={model.id} value={model.nombre}>
                                {model.nombre}
                              </SelectItem>
                            ))}
                        </SelectContent>
                      </Select>
                      {showNewModel && (
                        <div className="mt-2 flex gap-2">
                          <Input
                            placeholder="Nuevo modelo"
                            value={newModel}
                            onChange={(e) => setNewModel(e.target.value)}
                          />
                          <Button type="button" onClick={addModel}>Agregar</Button>
                          <Button type="button" variant="outline" onClick={() => setShowNewModel(false)}>Cancelar</Button>
                        </div>
                      )}
                    </div>

                    <div>
                      <Label>ATO (opcional)</Label>
                      <Input
                        value={equipmentForm.ato}
                        onChange={(e) => setEquipmentForm({...equipmentForm, ato: e.target.value})}
                      />
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <Label>Fabricante</Label>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowNewManufacturer(true)}
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                      <Select onValueChange={(value) => setEquipmentForm({...equipmentForm, fabricante: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar fabricante" />
                        </SelectTrigger>
                        <SelectContent>
                          {manufacturers.map((manufacturer) => (
                            <SelectItem key={manufacturer.id} value={manufacturer.nombre}>
                              {manufacturer.nombre}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {showNewManufacturer && (
                        <div className="mt-2 flex gap-2">
                          <Input
                            placeholder="Nuevo fabricante"
                            value={newManufacturer}
                            onChange={(e) => setNewManufacturer(e.target.value)}
                          />
                          <Button type="button" onClick={addManufacturer}>Agregar</Button>
                          <Button type="button" variant="outline" onClick={() => setShowNewManufacturer(false)}>Cancelar</Button>
                        </div>
                      )}
                    </div>

                    <div>
                      <Label>Número de Serie</Label>
                      <Input
                        value={equipmentForm.numero_serie}
                        onChange={(e) => setEquipmentForm({...equipmentForm, numero_serie: e.target.value})}
                        required
                      />
                    </div>

                    <div>
                      <Label>Fecha de Fabricación (opcional)</Label>
                      <Input
                        type="date"
                        value={equipmentForm.fecha_fabricacion}
                        onChange={(e) => setEquipmentForm({...equipmentForm, fecha_fabricacion: e.target.value})}
                      />
                    </div>

                    <div>
                      <Label>Tipo de Fallo</Label>
                      <Select onValueChange={(value) => setEquipmentForm({...equipmentForm, tipo_fallo: value})}>
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar tipo de fallo" />
                        </SelectTrigger>
                        <SelectContent>
                          {faultTypes.map((faultType) => (
                            <SelectItem key={faultType.id} value={faultType.nombre}>
                              {faultType.nombre}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {requiresSensorInfo() && (
                      <>
                        <div>
                          <Label>Número de Serie del Sensor</Label>
                          <Input
                            value={equipmentForm.numero_serie_sensor}
                            onChange={(e) => setEquipmentForm({...equipmentForm, numero_serie_sensor: e.target.value})}
                            required
                          />
                        </div>
                        <div>
                          <Label>Fecha de Instalación del Sensor</Label>
                          <Input
                            type="date"
                            value={equipmentForm.fecha_instalacion_sensor}
                            onChange={(e) => setEquipmentForm({...equipmentForm, fecha_instalacion_sensor: e.target.value})}
                          />
                        </div>
                      </>
                    )}

                    <div className="md:col-span-2">
                      <Label>Observaciones</Label>
                      <Textarea
                        value={equipmentForm.observaciones}
                        onChange={(e) => setEquipmentForm({...equipmentForm, observaciones: e.target.value})}
                        rows={3}
                      />
                    </div>

                    <div className="md:col-span-2">
                      <Button type="submit" className="w-full">
                        Registrar Equipo
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </div>
          )}

          {currentModule === 'gestion' && (
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">Gestión Administrativa de Envíos</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Equipos Pendientes de Envío</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Orden de Trabajo</TableHead>
                        <TableHead>Cliente</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Modelo</TableHead>
                        <TableHead>Número de Serie</TableHead>
                        <TableHead>Estado</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {equipment.filter(eq => eq.estado === 'Pendiente').map((eq) => (
                        <TableRow key={eq.id}>
                          <TableCell>{eq.orden_trabajo}</TableCell>
                          <TableCell>{eq.cliente_nombre}</TableCell>
                          <TableCell>{eq.tipo_equipo}</TableCell>
                          <TableCell>{eq.modelo}</TableCell>
                          <TableCell>{eq.numero_serie}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{eq.estado}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          )}

          {currentModule === 'respuesta' && (
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">Respuesta del Fabricante</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Equipos Enviados al Fabricante</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Orden de Trabajo</TableHead>
                        <TableHead>Cliente</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Orden de Compra</TableHead>
                        <TableHead>Estado</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {equipment.filter(eq => eq.estado === 'Enviado').map((eq) => (
                        <TableRow key={eq.id}>
                          <TableCell>{eq.orden_trabajo}</TableCell>
                          <TableCell>{eq.cliente_nombre}</TableCell>
                          <TableCell>{eq.tipo_equipo}</TableCell>
                          <TableCell>{eq.numero_orden_compra}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{eq.estado}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          )}

          {currentModule === 'recepcion' && (
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">Recepción en ASCONSA</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Equipos Pendientes de Recepción</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Orden de Trabajo</TableHead>
                        <TableHead>Cliente</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Estado</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {equipment.filter(eq => eq.estado === 'En Fabricante').map((eq) => (
                        <TableRow key={eq.id}>
                          <TableCell>{eq.orden_trabajo}</TableCell>
                          <TableCell>{eq.cliente_nombre}</TableCell>
                          <TableCell>{eq.tipo_equipo}</TableCell>
                          <TableCell>
                            <Badge variant="default">{eq.estado}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          )}

          {currentModule === 'completados' && (
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">Envíos Completados</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Equipos Recibidos en ASCONSA</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Orden de Trabajo</TableHead>
                        <TableHead>Cliente</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Modelo</TableHead>
                        <TableHead>Fabricante</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Fecha</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {equipment.filter(eq => eq.estado === 'Recibido').map((eq) => (
                        <TableRow key={eq.id}>
                          <TableCell>{eq.orden_trabajo}</TableCell>
                          <TableCell>{eq.cliente_nombre}</TableCell>
                          <TableCell>{eq.tipo_equipo}</TableCell>
                          <TableCell>{eq.modelo}</TableCell>
                          <TableCell>{eq.fabricante}</TableCell>
                          <TableCell>
                            <Badge variant="success">{eq.estado}</Badge>
                          </TableCell>
                          <TableCell>{new Date(eq.updated_at).toLocaleDateString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;