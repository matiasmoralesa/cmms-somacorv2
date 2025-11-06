import React, { useState, useRef } from 'react';
import { Upload, X, Eye, Plus, AlertCircle } from 'lucide-react';

interface ImageData {
  id: string;
  descripcion: string;
  imagen_base64: string;
  preview?: string;
}

interface MultipleImageUploadProps {
  images: ImageData[];
  onImagesChange: (images: ImageData[]) => void;
  maxImages?: number;
  maxSizeKB?: number;
  acceptedTypes?: string[];
  disabled?: boolean;
}

const MultipleImageUpload: React.FC<MultipleImageUploadProps> = ({
  images,
  onImagesChange,
  maxImages = 5,
  maxSizeKB = 2048, // 2MB por defecto
  acceptedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
  disabled = false
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateId = () => `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const validateFile = (file: File): string | null => {
    if (!acceptedTypes.includes(file.type)) {
      return `Tipo de archivo no permitido. Tipos aceptados: ${acceptedTypes.join(', ')}`;
    }
    
    if (file.size > maxSizeKB * 1024) {
      return `El archivo es muy grande. Tamaño máximo: ${maxSizeKB}KB`;
    }
    
    if (images.length >= maxImages) {
      return `Máximo ${maxImages} imágenes permitidas`;
    }
    
    return null;
  };

  const processFile = (file: File): Promise<ImageData> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result as string;
        resolve({
          id: generateId(),
          descripcion: '',
          imagen_base64: base64,
          preview: base64
        });
      };
      reader.onerror = () => reject(new Error('Error al leer el archivo'));
      reader.readAsDataURL(file);
    });
  };

  const handleFileSelect = async (files: FileList) => {
    setError(null);
    const newImages: ImageData[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const validationError = validateFile(file);
      
      if (validationError) {
        setError(validationError);
        continue;
      }
      
      try {
        const imageData = await processFile(file);
        newImages.push(imageData);
      } catch (err) {
        setError(`Error al procesar ${file.name}: ${err.message}`);
      }
    }
    
    if (newImages.length > 0) {
      onImagesChange([...images, ...newImages]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    if (disabled) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
    // Limpiar el input para permitir seleccionar el mismo archivo nuevamente
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeImage = (id: string) => {
    const updatedImages = images.filter(img => img.id !== id);
    onImagesChange(updatedImages);
  };

  const updateImageDescription = (id: string, descripcion: string) => {
    const updatedImages = images.map(img => 
      img.id === id ? { ...img, descripcion } : img
    );
    onImagesChange(updatedImages);
  };

  const openFileDialog = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="space-y-4">
      {/* Área de carga */}
      <div
        className={`
          border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-blue-400'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
          disabled={disabled}
        />
        
        <div className="flex flex-col items-center space-y-2">
          <Upload className="h-8 w-8 text-gray-400" />
          <div className="text-sm text-gray-600">
            <span className="font-medium">Haz clic para subir</span> o arrastra y suelta
          </div>
          <div className="text-xs text-gray-500">
            {acceptedTypes.join(', ')} hasta {maxSizeKB}KB cada una
          </div>
          <div className="text-xs text-gray-500">
            Máximo {maxImages} imágenes ({images.length}/{maxImages})
          </div>
        </div>
      </div>

      {/* Mostrar errores */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Lista de imágenes */}
      {images.length > 0 && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-700">Imágenes cargadas ({images.length})</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {images.map((image) => (
              <div key={image.id} className="border rounded-lg p-3 bg-white shadow-sm">
                <div className="flex items-start space-x-3">
                  {/* Miniatura */}
                  <div className="relative flex-shrink-0">
                    <img
                      src={image.preview || image.imagen_base64}
                      alt="Preview"
                      className="w-16 h-16 object-cover rounded border cursor-pointer"
                      onClick={() => setPreviewImage(image.preview || image.imagen_base64)}
                    />
                    <button
                      type="button"
                      onClick={() => setPreviewImage(image.preview || image.imagen_base64)}
                      className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 rounded flex items-center justify-center transition-opacity"
                    >
                      <Eye className="h-4 w-4 text-white opacity-0 hover:opacity-100" />
                    </button>
                  </div>
                  
                  {/* Descripción */}
                  <div className="flex-1 space-y-2">
                    <input
                      type="text"
                      placeholder="Descripción de la imagen (opcional)"
                      value={image.descripcion}
                      onChange={(e) => updateImageDescription(image.id, e.target.value)}
                      className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      disabled={disabled}
                    />
                    <div className="text-xs text-gray-500">
                      Tamaño: {Math.round(image.imagen_base64.length * 0.75 / 1024)}KB
                    </div>
                  </div>
                  
                  {/* Botón eliminar */}
                  <button
                    type="button"
                    onClick={() => removeImage(image.id)}
                    className="text-red-500 hover:text-red-700 p-1"
                    disabled={disabled}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal de preview */}
      {previewImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="relative max-w-4xl max-h-full">
            <button
              onClick={() => setPreviewImage(null)}
              className="absolute top-4 right-4 text-white hover:text-gray-300 z-10"
            >
              <X className="h-6 w-6" />
            </button>
            <img
              src={previewImage}
              alt="Preview"
              className="max-w-full max-h-full object-contain rounded"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default MultipleImageUpload;

