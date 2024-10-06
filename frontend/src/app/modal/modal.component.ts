import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import UIkit from 'uikit';

@Component({
  selector: 'app-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './modal.component.html',
  styleUrls: ['./modal.component.css']
})
export class ModalComponent {
  @Output() modalClosed = new EventEmitter<void>(); 

  openModal() {
    const modalElement = document.getElementById('modal-falha-upload');
    if (modalElement) {
      UIkit.modal(modalElement).show(); 
    }
  }

  onClose() {
    const modalElement = document.getElementById('modal-falha-upload');
    if (modalElement) {
      UIkit.modal(modalElement).hide();
      this.modalClosed.emit(); 
    }
  }
}
