import { Component, ViewChild } from '@angular/core';
import { ModalComponent } from '../modal/modal.component';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ApiService } from '../services/api.service';
import { HttpClientModule } from '@angular/common/http';
import { AuthService } from '../services/auth.service';
import { ToastrService } from 'ngx-toastr';
import { catchError, switchMap, throwError } from 'rxjs';
import { v4 as uuidv4 } from 'uuid';

@Component({
  selector: 'app-upload-image',
  standalone: true,
  imports: [CommonModule, ModalComponent, RouterModule, HttpClientModule],
  templateUrl: './upload-image.component.html',
  styleUrls: ['./upload-image.component.css']
})
export class UploadImageComponent {
  temArquivo: boolean = false;
  imagemSrc: string | null = null;
  selectedFile: File | null = null;
  isLoading: boolean = false;

  @ViewChild(ModalComponent) modal!: ModalComponent;

  constructor(
    private router: Router,
    private apiService: ApiService,
    private authService: AuthService,
    private toastr: ToastrService
  ) {}

  triggerFileUpload() {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fileInput.value = '';
    fileInput.click();
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    this.temArquivo = false;
    this.selectedFile = null;

    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];

      if (!allowedTypes.includes(file.type)) {
        this.modal.openModal();
        this.toastr.error('Tipo de arquivo não suportado. Use JPEG, PNG ou GIF.', 'Erro');
        return;
      }

      this.temArquivo = true;
      this.selectedFile = file;

      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagemSrc = e.target.result;
      };
      reader.readAsDataURL(file);

      this.toastr.success('Imagem carregada com sucesso!', 'Sucesso');
    }
  }

  resetFileInput() {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fileInput.value = '';
    this.temArquivo = false;
    this.imagemSrc = null;
    this.selectedFile = null;
    this.toastr.info('Imagem removida', 'Aviso');
  }

  analyzeImage(analysisType: 'object' | 'composition') {
    if (!this.selectedFile) {
      this.toastr.warning('Selecione uma imagem antes de analisar', 'Atenção');
      return;
    }

    if (analysisType !== 'object') {
      this.toastr.info('Análise de composição estará disponível em breve', 'Em desenvolvimento');
      return;
    }

    this.checkAuthAndAnalyze();
  }

  private checkAuthAndAnalyze() {
    this.isLoading = true;

    this.authService.isAuthenticated().pipe(
      switchMap(authResponse => {
        if (!authResponse.authenticated) {
          return throwError(() => ({ status: 401, message: 'Não autenticado' }));
        }
        return this.performImageAnalysis();
      }),
      catchError(error => {
        this.handleAuthError(error);
        return throwError(() => error);
      })
    ).subscribe({
      next: (response) => {
        this.handleAnalysisSuccess(response);
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  private performImageAnalysis() {
    this.toastr.info('Analisando imagem...', 'Processando');
    const formData = new FormData();
    formData.append('image', this.selectedFile!);

    const imageUuid = uuidv4();

    formData.append('uuid', imageUuid);

    return this.apiService.post<any>('neural/analyze', formData, {
      Authorization: `Bearer ${this.authService.getAccessToken()}`
    });
  }

  private handleAuthError(error: any) {
    if (error.status == 401 || error.error?.authenticated == false) {
      this.toastr.error('Sessão expirada. Faça login novamente.', 'Erro');
      this.authService.logout();
      this.router.navigate(['/login']);
    } else {
      console.error('Erro de autenticação:', error);
      this.toastr.error('Erro ao verificar autenticação', 'Erro');
    }
  }

  private handleAnalysisSuccess(response: any) {
    this.isLoading = false;
    const processedImageUrl = response.data.image_url;
    this.router.navigate(['/result-image'], {
      state: {
        analysisData: response.data,
        originalImage: processedImageUrl,
        analysisType: 'object'
      }
    });
  }
}
