import { Component, ViewChild, AfterViewInit } from '@angular/core';
import { ModalComponent } from '../modal/modal.component'; 
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-upload-image',
  standalone: true,
  imports: [CommonModule, ModalComponent, RouterModule],
  templateUrl: './upload-image.component.html',
  styleUrls: ['./upload-image.component.css']
})
export class UploadImageComponent implements AfterViewInit {
  temArquivo: boolean = false;
  imagemSrc: string | null = null;  

  @ViewChild(ModalComponent) modal!: ModalComponent; 

  ngAfterViewInit() {
    if (!this.modal) {
      console.error('Modal component is not initialized');
    } else {
      console.log('Modal component initialized successfully');
      this.modal.modalClosed.subscribe(() => {
        this.resetFileInput();
      });
    }
  }

  triggerFileUpload() {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fileInput.value = '';
    fileInput.click(); 
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    this.temArquivo = false; 
  
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    
      if (!allowedTypes.includes(file.type)) {
        this.modal.openModal(); 
        return; 
      }
    
      this.temArquivo = true; 
      console.log('Arquivo selecionado:', file.name);

      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.imagemSrc = e.target.result;  
      };
      reader.readAsDataURL(file);  
    }
  }

  resetFileInput() {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    fileInput.value = ''; 
    this.temArquivo = false; 
    this.imagemSrc = null;
  }
}
