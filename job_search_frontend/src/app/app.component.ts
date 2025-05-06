import { Component } from '@angular/core';
import { LoaderService } from './shared/loader/loader.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'job_search_frontend';
  isLoading: boolean = false;

  constructor(public loaderService: LoaderService) {}

  
}

