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
  Download,
  Building2
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
  const [activePurchaseOrders, setActivePurchaseOrders] = useState([]);
  const [selectedClientWorkCenters, setSelectedClientWorkCenters] = useState([]);

  // Administrative management states
  const [selectedEquipment, setSelectedEquipment] = useState([]);
  const [purchaseOrderNumber, setPurchaseOrderNumber] = useState('');
  const [selectedPurchaseOrder, setSelectedPurchaseOrder] = useState('');
  const [purchaseOrderEquipment, setPurchaseOrderEquipment] = useState([]);

  // Manufacturer response states
  const [manufacturerSelectedPO, setManufacturerSelectedPO] = useState('');
  const [manufacturerPOEquipment, setManufacturerPOEquipment] = useState([]);
  const [selectedManufacturerEquipment, setSelectedManufacturerEquipment] = useState([]);
  const [receptionNumber, setReceptionNumber] = useState('');
  const [isUnderWarranty, setIsUnderWarranty] = useState(true);
  const [quoteNumber, setQuoteNumber] = useState('');
  const [quoteAccepted, setQuoteAccepted] = useState(false);

  // Reception states
  const [receptionEquipment, setReceptionEquipment] = useState([]);
  const [selectedReceptionEquipment, setSelectedReceptionEquipment] = useState([]);

  // Completed equipment states
  const [completedEquipment, setCompletedEquipment] = useState([]);

  // Form states
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [equipmentForm, setEquipmentForm] = useState({
    orden_trabajo: '',
    cliente_id: '',
    cliente_nombre: '',
    centro_trabajo_id: '',
    centro_trabajo_nombre: '',
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
    email: '',
    centros_trabajo: []
  });

  const [workCenterForm, setWorkCenterForm] = useState({
    nombre: '',
    direccion: '',
    telefono: ''
  });

  const [showClientDialog, setShowClientDialog] = useState(false);
  const [showEditClientDialog, setShowEditClientDialog] = useState(false);
  const [showClientsListDialog, setShowClientsListDialog] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [showWorkCenterDialog, setShowWorkCenterDialog] = useState(false);
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

  const loadActivePurchaseOrders = async () => {
    try {
      const response = await axios.get(`${API}/ordenes-compra/activas`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActivePurchaseOrders(response.data.active_orders);
    } catch (error) {
      console.error('Error loading active purchase orders:', error);
    }
  };

  const loadClientWorkCenters = async (clientId) => {
    try {
      const response = await axios.get(`${API}/clientes/${clientId}/centros-trabajo`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedClientWorkCenters(response.data);
    } catch (error) {
      console.error('Error loading client work centers:', error);
      setSelectedClientWorkCenters([]);
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

  const addWorkCenter = () => {
    if (!workCenterForm.nombre.trim()) {
      alert('Por favor ingrese el nombre del centro de trabajo');
      return;
    }
    
    const newWorkCenter = {
      id: `wc-${Date.now()}`,
      nombre: workCenterForm.nombre,
      direccion: workCenterForm.direccion,
      telefono: workCenterForm.telefono
    };
    
    // If editing an existing client, call API to add work center
    if (editingClient && showEditClientDialog) {
      addWorkCenterToExistingClient(editingClient.id, newWorkCenter).then((success) => {
        if (success) {
          setWorkCenterForm({ nombre: '', direccion: '', telefono: '' });
          setShowWorkCenterDialog(false);
        }
      });
    } else {
      // Adding to new client form (creating new client)
      setClientForm({
        ...clientForm,
        centros_trabajo: [...clientForm.centros_trabajo, newWorkCenter]
      });
      setWorkCenterForm({ nombre: '', direccion: '', telefono: '' });
      setShowWorkCenterDialog(false);
    }
  };

  const removeWorkCenter = (workCenterId) => {
    // If editing an existing client, call API to remove work center
    if (editingClient && showEditClientDialog) {
      removeWorkCenterFromExistingClient(editingClient.id, workCenterId);
    } else {
      // Removing from new client form (creating new client)
      setClientForm({
        ...clientForm,
        centros_trabajo: clientForm.centros_trabajo.filter(wc => wc.id !== workCenterId)
      });
    }
  };

  const createClient = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/clientes`, clientForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setClients([...clients, response.data]);
      resetClientForm();
      setShowClientDialog(false);
      alert('Cliente creado correctamente');
    } catch (error) {
      console.error('Error creating client:', error);
      alert('Error al crear cliente');
    }
  };

  const editClient = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`${API}/clientes/${editingClient.id}`, clientForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update clients list
      setClients(clients.map(c => c.id === editingClient.id ? response.data : c));
      
      // Reset form and close dialogs
      resetClientForm();
      setShowEditClientDialog(false);
      setShowClientsListDialog(false);
      
      alert('Cliente actualizado correctamente');
    } catch (error) {
      console.error('Error updating client:', error);
      alert('Error al actualizar cliente');
    }
  };

  const openEditClientDialog = (client) => {
    setEditingClient(client);
    setClientForm({
      nombre: client.nombre,
      cif: client.cif,
      telefono: client.telefono,
      email: client.email || '',
      centros_trabajo: client.centros_trabajo || []
    });
    setShowClientsListDialog(false);
    setShowEditClientDialog(true);
  };

  const resetClientForm = () => {
    setClientForm({ nombre: '', cif: '', telefono: '', email: '', centros_trabajo: [] });
    setWorkCenterForm({ nombre: '', direccion: '', telefono: '' });
    setEditingClient(null);
  };

  const addWorkCenterToExistingClient = async (clientId, workCenter) => {
    try {
      const response = await axios.post(`${API}/clientes/${clientId}/centros-trabajo`, workCenter, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update the editing client data
      setEditingClient(response.data);
      setClientForm({
        ...clientForm,
        centros_trabajo: response.data.centros_trabajo
      });
      
      return true;
    } catch (error) {
      console.error('Error adding work center:', error);
      alert('Error al agregar centro de trabajo');
      return false;
    }
  };

  const removeWorkCenterFromExistingClient = async (clientId, workCenterId) => {
    try {
      await axios.delete(`${API}/clientes/${clientId}/centros-trabajo/${workCenterId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update the editing client data
      const updatedClient = {
        ...editingClient,
        centros_trabajo: editingClient.centros_trabajo.filter(wc => wc.id !== workCenterId)
      };
      
      setEditingClient(updatedClient);
      setClientForm({
        ...clientForm,
        centros_trabajo: updatedClient.centros_trabajo
      });
      
      return true;
    } catch (error) {
      console.error('Error removing work center:', error);
      alert('Error al eliminar centro de trabajo');
      return false;
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
        centro_trabajo_id: '',
        centro_trabajo_nombre: '',
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

  const assignPurchaseOrder = async () => {
    if (!purchaseOrderNumber || selectedEquipment.length === 0) {
      alert('Por favor ingrese un número de pedido y seleccione equipos');
      return;
    }

    try {
      const response = await axios.post(`${API}/ordenes-compra/asignar`, {
        numero_orden: purchaseOrderNumber,
        equipment_ids: selectedEquipment
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert(`${response.data.assigned_count} equipos asignados a la orden de compra ${purchaseOrderNumber}`);
      
      // Refresh equipment list
      const equipmentRes = await axios.get(`${API}/equipos`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEquipment(equipmentRes.data);
      
      // Refresh active purchase orders
      loadActivePurchaseOrders();
      
      // Reset form
      setSelectedEquipment([]);
      setPurchaseOrderNumber('');
    } catch (error) {
      console.error('Error assigning purchase order:', error);
      alert('Error al asignar orden de compra');
    }
  };

  const loadPurchaseOrderEquipment = async (orderNumber) => {
    try {
      const response = await axios.get(`${API}/ordenes-compra/${orderNumber}/equipos`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPurchaseOrderEquipment(response.data);
    } catch (error) {
      console.error('Error loading purchase order equipment:', error);
    }
  };

  const loadManufacturerPOEquipment = async (orderNumber) => {
    try {
      const response = await axios.get(`${API}/ordenes-compra/${orderNumber}/equipos/enviados`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setManufacturerPOEquipment(response.data);
    } catch (error) {
      console.error('Error loading manufacturer PO equipment:', error);
    }
  };

  const submitManufacturerResponse = async () => {
    if (!manufacturerSelectedPO || selectedManufacturerEquipment.length === 0 || !receptionNumber) {
      alert('Por favor complete todos los campos requeridos');
      return;
    }

    try {
      const response = await axios.post(`${API}/ordenes-compra/${manufacturerSelectedPO}/respuesta-fabricante`, {
        equipment_ids: selectedManufacturerEquipment,
        numero_recepcion_fabricante: receptionNumber,
        en_garantia: isUnderWarranty,
        numero_presupuesto: !isUnderWarranty ? quoteNumber : null,
        presupuesto_aceptado: !isUnderWarranty ? quoteAccepted : null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert(`Respuesta de fabricante registrada para ${response.data.updated_count} equipos`);
      
      // Refresh the equipment list for this PO
      loadManufacturerPOEquipment(manufacturerSelectedPO);
      
      // Reset form
      setSelectedManufacturerEquipment([]);
      setReceptionNumber('');
      setIsUnderWarranty(true);
      setQuoteNumber('');
      setQuoteAccepted(false);
    } catch (error) {
      console.error('Error submitting manufacturer response:', error);
      alert('Error al registrar respuesta de fabricante');
    }
  };

  const loadReceptionEquipment = async () => {
    try {
      const response = await axios.get(`${API}/equipos/para-recepcion`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReceptionEquipment(response.data);
    } catch (error) {
      console.error('Error loading reception equipment:', error);
    }
  };

  const receiveEquipment = async () => {
    if (selectedReceptionEquipment.length === 0) {
      alert('Por favor seleccione equipos para marcar como recibidos');
      return;
    }

    try {
      const response = await axios.post(`${API}/equipos/recibir`, {
        equipment_ids: selectedReceptionEquipment
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      alert(`${response.data.received_count} equipos marcados como recibidos`);
      
      // Refresh reception equipment list
      loadReceptionEquipment();
      
      // Reset selection
      setSelectedReceptionEquipment([]);
    } catch (error) {
      console.error('Error receiving equipment:', error);
      alert('Error al marcar equipos como recibidos');
    }
  };

  const loadCompletedEquipment = async () => {
    try {
      const response = await axios.get(`${API}/equipos/completados`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCompletedEquipment(response.data);
    } catch (error) {
      console.error('Error loading completed equipment:', error);
    }
  };

  const exportToCSV = async (orderNumber) => {
    try {
      const response = await axios.get(`${API}/ordenes-compra/${orderNumber}/export-csv`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Create and download CSV file
      const blob = new Blob([response.data.content], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting CSV:', error);
      alert('Error al exportar CSV');
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
        cliente_nombre: selectedClient.nombre,
        centro_trabajo_id: '',
        centro_trabajo_nombre: ''
      });
      
      // Load work centers for this client
      loadClientWorkCenters(clientId);
    }
  };

  const handleWorkCenterSelect = (workCenterId) => {
    if (!workCenterId) {
      setEquipmentForm({
        ...equipmentForm,
        centro_trabajo_id: '',
        centro_trabajo_nombre: ''
      });
      return;
    }
    
    const selectedWorkCenter = selectedClientWorkCenters.find(wc => wc.id === workCenterId);
    if (selectedWorkCenter) {
      setEquipmentForm({
        ...equipmentForm,
        centro_trabajo_id: workCenterId,
        centro_trabajo_nombre: selectedWorkCenter.nombre
      });
    }
  };

  const handleEquipmentSelection = (equipmentId, checked) => {
    if (checked) {
      setSelectedEquipment([...selectedEquipment, equipmentId]);
    } else {
      setSelectedEquipment(selectedEquipment.filter(id => id !== equipmentId));
    }
  };

  const handleManufacturerEquipmentSelection = (equipmentId, checked) => {
    if (checked) {
      setSelectedManufacturerEquipment([...selectedManufacturerEquipment, equipmentId]);
    } else {
      setSelectedManufacturerEquipment(selectedManufacturerEquipment.filter(id => id !== equipmentId));
    }
  };

  const handleReceptionEquipmentSelection = (equipmentId, checked) => {
    if (checked) {
      setSelectedReceptionEquipment([...selectedReceptionEquipment, equipmentId]);
    } else {
      setSelectedReceptionEquipment(selectedReceptionEquipment.filter(id => id !== equipmentId));
    }
  };

  const requiresSensorInfo = () => {
    const selectedFaultType = faultTypes.find(ft => ft.nombre === equipmentForm.tipo_fallo);
    return selectedFaultType?.requiere_sensor && equipmentForm.tipo_equipo === 'Detector Portátil de Gas';
  };

  // Load data when switching modules
  useEffect(() => {
    if (token) {
      switch (currentModule) {
        case 'gestion':
          loadActivePurchaseOrders();
          break;
        case 'respuesta':
          loadActivePurchaseOrders();
          break;
        case 'recepcion':
          loadReceptionEquipment();
          break;
        case 'completados':
          loadCompletedEquipment();
          break;
        default:
          break;
      }
    }
  }, [currentModule, token]);

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
                <div className="flex gap-2">
                  <Dialog open={showClientDialog} onOpenChange={(open) => {
                    setShowClientDialog(open);
                    if (!open) resetClientForm();
                  }}>
                    <DialogTrigger asChild>
                      <Button>
                        <Plus className="h-4 w-4 mr-2" />
                        Nuevo Cliente
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>Agregar Nuevo Cliente</DialogTitle>
                      </DialogHeader>
                      <form onSubmit={createClient} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
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
                        </div>
                        
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <Label className="text-lg font-medium">Centros de Trabajo</Label>
                            <Dialog open={showWorkCenterDialog} onOpenChange={setShowWorkCenterDialog}>
                              <DialogTrigger asChild>
                                <Button type="button" variant="outline" size="sm">
                                  <Building2 className="h-4 w-4 mr-2" />
                                  Agregar Centro
                                </Button>
                              </DialogTrigger>
                              <DialogContent>
                                <DialogHeader>
                                  <DialogTitle>Agregar Centro de Trabajo</DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <div>
                                    <Label>Nombre del Centro</Label>
                                    <Input
                                      value={workCenterForm.nombre}
                                      onChange={(e) => setWorkCenterForm({...workCenterForm, nombre: e.target.value})}
                                      placeholder="Ej: Sede Central, Almacén Norte..."
                                    />
                                  </div>
                                  <div>
                                    <Label>Dirección (opcional)</Label>
                                    <Input
                                      value={workCenterForm.direccion}
                                      onChange={(e) => setWorkCenterForm({...workCenterForm, direccion: e.target.value})}
                                      placeholder="Dirección completa"
                                    />
                                  </div>
                                  <div>
                                    <Label>Teléfono (opcional)</Label>
                                    <Input
                                      value={workCenterForm.telefono}
                                      onChange={(e) => setWorkCenterForm({...workCenterForm, telefono: e.target.value})}
                                      placeholder="Teléfono del centro"
                                    />
                                  </div>
                                  <Button type="button" onClick={addWorkCenter} className="w-full">
                                    Agregar Centro
                                  </Button>
                                </div>
                              </DialogContent>
                            </Dialog>
                          </div>
                          
                          {clientForm.centros_trabajo.length > 0 && (
                            <div className="border rounded-lg p-3 bg-slate-50">
                              {clientForm.centros_trabajo.map((wc) => (
                                <div key={wc.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                                  <div>
                                    <div className="font-medium">{wc.nombre}</div>
                                    {wc.direccion && <div className="text-sm text-slate-600">{wc.direccion}</div>}
                                    {wc.telefono && <div className="text-sm text-slate-600">Tel: {wc.telefono}</div>}
                                  </div>
                                  <Button 
                                    type="button"
                                    variant="ghost" 
                                    size="sm"
                                    onClick={() => removeWorkCenter(wc.id)}
                                  >
                                    Eliminar
                                  </Button>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <Button type="submit">Guardar Cliente</Button>
                      </form>
                    </DialogContent>
                  </Dialog>
                  
                  <Dialog open={showClientsListDialog} onOpenChange={setShowClientsListDialog}>
                    <DialogTrigger asChild>
                      <Button variant="outline">
                        <Users className="h-4 w-4 mr-2" />
                        Editar Cliente
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Seleccionar Cliente a Editar</DialogTitle>
                      </DialogHeader>
                      <div className="max-h-96 overflow-y-auto">
                        {clients.map((client) => (
                          <div key={client.id} className="flex items-center justify-between p-3 border rounded-lg mb-2">
                            <div>
                              <div className="font-medium">{client.nombre}</div>
                              <div className="text-sm text-slate-600">CIF: {client.cif}</div>
                              <div className="text-sm text-slate-600">
                                {client.centros_trabajo?.length || 0} centro(s) de trabajo
                              </div>
                            </div>
                            <Button 
                              size="sm"
                              onClick={() => openEditClientDialog(client)}
                            >
                              Editar
                            </Button>
                          </div>
                        ))}
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>

              {/* Edit Client Dialog */}
              <Dialog open={showEditClientDialog} onOpenChange={(open) => {
                setShowEditClientDialog(open);
                if (!open) resetClientForm();
              }}>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Editar Cliente: {editingClient?.nombre}</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={editClient} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
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
                    </div>
                    
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <Label className="text-lg font-medium">Centros de Trabajo</Label>
                        <Dialog open={showWorkCenterDialog} onOpenChange={setShowWorkCenterDialog}>
                          <DialogTrigger asChild>
                            <Button type="button" variant="outline" size="sm">
                              <Building2 className="h-4 w-4 mr-2" />
                              Agregar Centro
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Agregar Centro de Trabajo</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <Label>Nombre del Centro</Label>
                                <Input
                                  value={workCenterForm.nombre}
                                  onChange={(e) => setWorkCenterForm({...workCenterForm, nombre: e.target.value})}
                                  placeholder="Ej: Sede Central, Almacén Norte..."
                                />
                              </div>
                              <div>
                                <Label>Dirección (opcional)</Label>
                                <Input
                                  value={workCenterForm.direccion}
                                  onChange={(e) => setWorkCenterForm({...workCenterForm, direccion: e.target.value})}
                                  placeholder="Dirección completa"
                                />
                              </div>
                              <div>
                                <Label>Teléfono (opcional)</Label>
                                <Input
                                  value={workCenterForm.telefono}
                                  onChange={(e) => setWorkCenterForm({...workCenterForm, telefono: e.target.value})}
                                  placeholder="Teléfono del centro"
                                />
                              </div>
                              <Button type="button" onClick={addWorkCenter} className="w-full">
                                Agregar Centro
                              </Button>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </div>
                      
                      {clientForm.centros_trabajo.length > 0 && (
                        <div className="border rounded-lg p-3 bg-slate-50">
                          {clientForm.centros_trabajo.map((wc) => (
                            <div key={wc.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                              <div>
                                <div className="font-medium">{wc.nombre}</div>
                                {wc.direccion && <div className="text-sm text-slate-600">{wc.direccion}</div>}
                                {wc.telefono && <div className="text-sm text-slate-600">Tel: {wc.telefono}</div>}
                              </div>
                              <Button 
                                type="button"
                                variant="ghost" 
                                size="sm"
                                onClick={() => removeWorkCenter(wc.id)}
                              >
                                Eliminar
                              </Button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button type="submit">Actualizar Cliente</Button>
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => setShowEditClientDialog(false)}
                      >
                        Cancelar
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>

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

                    {selectedClientWorkCenters.length > 0 && (
                      <div>
                        <Label>Centro de Trabajo (opcional)</Label>
                        <Select onValueChange={handleWorkCenterSelect}>
                          <SelectTrigger>
                            <SelectValue placeholder="Seleccionar centro de trabajo" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="">Sin centro específico</SelectItem>
                            {selectedClientWorkCenters.map((workCenter) => (
                              <SelectItem key={workCenter.id} value={workCenter.id}>
                                {workCenter.nombre}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

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
              
              {/* Assign Purchase Order Section */}
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle>Asignar Número de Pedido</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 mb-4">
                    <Input
                      placeholder="Número de Pedido"
                      value={purchaseOrderNumber}
                      onChange={(e) => setPurchaseOrderNumber(e.target.value)}
                    />
                    <Button onClick={assignPurchaseOrder} disabled={selectedEquipment.length === 0}>
                      Asignar a {selectedEquipment.length} equipo(s)
                    </Button>
                  </div>
                  
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead></TableHead>
                        <TableHead>Orden de Trabajo</TableHead>
                        <TableHead>Cliente</TableHead>
                        <TableHead>Centro de Trabajo</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Modelo</TableHead>
                        <TableHead>Número de Serie</TableHead>
                        <TableHead>Estado</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {equipment.filter(eq => eq.estado === 'Pendiente').map((eq) => (
                        <TableRow key={eq.id}>
                          <TableCell>
                            <Checkbox
                              checked={selectedEquipment.includes(eq.id)}
                              onCheckedChange={(checked) => handleEquipmentSelection(eq.id, checked)}
                            />
                          </TableCell>
                          <TableCell>{eq.orden_trabajo}</TableCell>
                          <TableCell>{eq.cliente_nombre}</TableCell>
                          <TableCell>{eq.centro_trabajo_nombre || '-'}</TableCell>
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

              {/* View by Purchase Order Section */}
              <Card>
                <CardHeader>
                  <CardTitle>Ver Equipos por Número de Pedido</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-4 mb-4">
                    <Select onValueChange={(value) => {
                      setSelectedPurchaseOrder(value);
                      loadPurchaseOrderEquipment(value);
                    }}>
                      <SelectTrigger className="w-64">
                        <SelectValue placeholder="Seleccionar número de pedido" />
                      </SelectTrigger>
                      <SelectContent>
                        {activePurchaseOrders.map((orderNumber) => (
                          <SelectItem key={orderNumber} value={orderNumber}>
                            {orderNumber}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {selectedPurchaseOrder && (
                      <Button onClick={() => exportToCSV(selectedPurchaseOrder)}>
                        <Download className="h-4 w-4 mr-2" />
                        Exportar CSV
                      </Button>
                    )}
                  </div>

                  {purchaseOrderEquipment.length > 0 && (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Orden de Trabajo</TableHead>
                          <TableHead>Cliente</TableHead>
                          <TableHead>Centro de Trabajo</TableHead>
                          <TableHead>Tipo</TableHead>
                          <TableHead>Modelo</TableHead>
                          <TableHead>Fabricante</TableHead>
                          <TableHead>Número de Serie</TableHead>
                          <TableHead>Estado</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {purchaseOrderEquipment.map((eq) => (
                          <TableRow key={eq.id}>
                            <TableCell>{eq.orden_trabajo}</TableCell>
                            <TableCell>{eq.cliente_nombre}</TableCell>
                            <TableCell>{eq.centro_trabajo_nombre || '-'}</TableCell>
                            <TableCell>{eq.tipo_equipo}</TableCell>
                            <TableCell>{eq.modelo}</TableCell>
                            <TableCell>{eq.fabricante}</TableCell>
                            <TableCell>{eq.numero_serie}</TableCell>
                            <TableCell>
                              <Badge variant="outline">{eq.estado}</Badge>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {currentModule === 'respuesta' && (
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">Respuesta del Fabricante</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Procesar Respuesta del Fabricante</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Purchase Order Selection */}
                    <div>
                      <Label>Seleccionar Número de Pedido</Label>
                      <Select onValueChange={(value) => {
                        setManufacturerSelectedPO(value);
                        loadManufacturerPOEquipment(value);
                      }}>
                        <SelectTrigger className="w-64">
                          <SelectValue placeholder="Seleccionar número de pedido" />
                        </SelectTrigger>
                        <SelectContent>
                          {activePurchaseOrders.map((orderNumber) => (
                            <SelectItem key={orderNumber} value={orderNumber}>
                              {orderNumber}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {manufacturerPOEquipment.length > 0 && (
                      <>
                        {/* Equipment Selection */}
                        <div>
                          <Label className="text-lg font-medium">Equipos Disponibles para Procesar</Label>
                          <Table className="mt-4">
                            <TableHeader>
                              <TableRow>
                                <TableHead></TableHead>
                                <TableHead>Orden de Trabajo</TableHead>
                                <TableHead>Cliente</TableHead>
                                <TableHead>Centro de Trabajo</TableHead>
                                <TableHead>Tipo</TableHead>
                                <TableHead>Número de Serie</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {manufacturerPOEquipment.map((eq) => (
                                <TableRow key={eq.id}>
                                  <TableCell>
                                    <Checkbox
                                      checked={selectedManufacturerEquipment.includes(eq.id)}
                                      onCheckedChange={(checked) => handleManufacturerEquipmentSelection(eq.id, checked)}
                                    />
                                  </TableCell>
                                  <TableCell>{eq.orden_trabajo}</TableCell>
                                  <TableCell>{eq.cliente_nombre}</TableCell>
                                  <TableCell>{eq.centro_trabajo_nombre || '-'}</TableCell>
                                  <TableCell>{eq.tipo_equipo}</TableCell>
                                  <TableCell>{eq.numero_serie}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </div>

                        {/* Manufacturer Response Form */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 border rounded-lg bg-slate-50">
                          <div>
                            <Label>Número de Recepción en Fabricante</Label>
                            <Input
                              value={receptionNumber}
                              onChange={(e) => setReceptionNumber(e.target.value)}
                              placeholder="Ej: REC-2024-001"
                            />
                          </div>

                          <div className="flex items-center space-x-2">
                            <Checkbox
                              id="warranty"
                              checked={isUnderWarranty}
                              onCheckedChange={setIsUnderWarranty}
                            />
                            <Label htmlFor="warranty">En Garantía</Label>
                          </div>

                          {!isUnderWarranty && (
                            <>
                              <div>
                                <Label>Número de Presupuesto</Label>
                                <Input
                                  value={quoteNumber}
                                  onChange={(e) => setQuoteNumber(e.target.value)}
                                  placeholder="Ej: PRES-2024-001"
                                />
                              </div>

                              <div className="flex items-center space-x-2">
                                <Checkbox
                                  id="quoteAccepted"
                                  checked={quoteAccepted}
                                  onCheckedChange={setQuoteAccepted}
                                />
                                <Label htmlFor="quoteAccepted">Presupuesto Aceptado</Label>
                              </div>
                            </>
                          )}

                          <div className="md:col-span-2">
                            <Button 
                              onClick={submitManufacturerResponse}
                              disabled={selectedManufacturerEquipment.length === 0 || !receptionNumber}
                              className="w-full"
                            >
                              Registrar Respuesta para {selectedManufacturerEquipment.length} equipo(s)
                            </Button>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentModule === 'recepcion' && (
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">Recepción en ASCONSA</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Equipos Listos para Recepción</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <Button 
                      onClick={receiveEquipment}
                      disabled={selectedReceptionEquipment.length === 0}
                      className="mb-4"
                    >
                      Marcar como Recibidos ({selectedReceptionEquipment.length} equipo(s))
                    </Button>

                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead></TableHead>
                          <TableHead>Orden de Trabajo</TableHead>
                          <TableHead>Cliente</TableHead>
                          <TableHead>Centro de Trabajo</TableHead>
                          <TableHead>Tipo</TableHead>
                          <TableHead>Número de Serie</TableHead>
                          <TableHead>Recepción Fabricante</TableHead>
                          <TableHead>Garantía</TableHead>
                          <TableHead>Presupuesto</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {receptionEquipment.map((eq) => (
                          <TableRow key={eq.id}>
                            <TableCell>
                              <Checkbox
                                checked={selectedReceptionEquipment.includes(eq.id)}
                                onCheckedChange={(checked) => handleReceptionEquipmentSelection(eq.id, checked)}
                              />
                            </TableCell>
                            <TableCell>{eq.orden_trabajo}</TableCell>
                            <TableCell>{eq.cliente_nombre}</TableCell>
                            <TableCell>{eq.centro_trabajo_nombre || '-'}</TableCell>
                            <TableCell>{eq.tipo_equipo}</TableCell>
                            <TableCell>{eq.numero_serie}</TableCell>
                            <TableCell>{eq.numero_recepcion_fabricante}</TableCell>
                            <TableCell>
                              <Badge variant={eq.en_garantia ? "success" : "secondary"}>
                                {eq.en_garantia ? "Sí" : "No"}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {eq.numero_presupuesto && (
                                <div>
                                  <div>{eq.numero_presupuesto}</div>
                                  <Badge variant={eq.presupuesto_aceptado ? "success" : "destructive"}>
                                    {eq.presupuesto_aceptado ? "Aceptado" : "Rechazado"}
                                  </Badge>
                                </div>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {currentModule === 'completados' && (
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-slate-800 mb-6">Envíos Completados</h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Equipos Recibidos en ASCONSA - Proceso Completado</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Orden de Trabajo</TableHead>
                        <TableHead>Cliente</TableHead>
                        <TableHead>Centro de Trabajo</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Modelo</TableHead>
                        <TableHead>Fabricante</TableHead>
                        <TableHead>Número de Serie</TableHead>
                        <TableHead>Orden Compra</TableHead>
                        <TableHead>Recepción Fabricante</TableHead>
                        <TableHead>Garantía</TableHead>
                        <TableHead>Presupuesto</TableHead>
                        <TableHead>Fecha Recepción</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {completedEquipment.map((eq) => (
                        <TableRow key={eq.id}>
                          <TableCell>{eq.orden_trabajo}</TableCell>
                          <TableCell>{eq.cliente_nombre}</TableCell>
                          <TableCell>{eq.centro_trabajo_nombre || '-'}</TableCell>
                          <TableCell>{eq.tipo_equipo}</TableCell>
                          <TableCell>{eq.modelo}</TableCell>
                          <TableCell>{eq.fabricante}</TableCell>
                          <TableCell>{eq.numero_serie}</TableCell>
                          <TableCell>{eq.numero_orden_compra}</TableCell>
                          <TableCell>{eq.numero_recepcion_fabricante}</TableCell>
                          <TableCell>
                            <Badge variant={eq.en_garantia ? "success" : "secondary"}>
                              {eq.en_garantia ? "Sí" : "No"}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {eq.numero_presupuesto && (
                              <div>
                                <div className="text-sm">{eq.numero_presupuesto}</div>
                                <Badge variant={eq.presupuesto_aceptado ? "success" : "destructive"}>
                                  {eq.presupuesto_aceptado ? "Aceptado" : "Rechazado"}
                                </Badge>
                              </div>
                            )}
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