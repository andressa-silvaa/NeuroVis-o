import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, NavigationStart, NavigationEnd } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { filter } from 'rxjs';

@Component({
  selector: 'app-result-image',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './result-image.component.html',
  styleUrls: ['./result-image.component.css']
})
export class ResultImageComponent {
  analysisData: any;
  originalImage: string | null = null;
  analysisType: string = 'object';
  isLoading: boolean = true; 

  constructor(private router: Router, private toastr: ToastrService) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationStart || event instanceof NavigationEnd)
    ).subscribe(event => {
      if (event instanceof NavigationStart) {
        this.isLoading = true;
      } else if (event instanceof NavigationEnd) {
        this.isLoading = false;
      }
    });

    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras.state as {
      analysisData: any;
      originalImage: string;
      analysisType: string;
    };

    if (state) {
      this.analysisData = state.analysisData;
      this.originalImage = state.originalImage;
      this.analysisType = state.analysisType;
      this.isLoading = false; 
      this.toastr.success('Análise carregada com sucesso!', 'Sucesso');
    } else {
      this.toastr.warning('Nenhum dado de análise encontrado', 'Aviso');
      this.router.navigate(['/upload-image']);
    }
  }

  getFormattedAccuracy(): string {
    if (!this.analysisData?.accuracy) return '0%';
    return `${(this.analysisData.accuracy * 100).toFixed(2)}%`;
  }

  getFormattedTime(timeInMs: number): string {
    if (timeInMs == undefined || timeInMs == null) return '0s';
    const timeInSeconds = (timeInMs / 1000).toFixed(2);  
    return `${timeInSeconds}s`;
  }

  getResultText(): string {
    if (!this.analysisData?.objects) return 'Nenhum objeto detectado';
    return this.analysisData.objects.join(', ');
  }

  goBack() {
    this.isLoading = true; 
    setTimeout(() => { 
      this.router.navigate(['/upload-image']); 
      setTimeout(() => {
        this.isLoading = false;  
      }, 1000);  
    }, 100);
  }
}
