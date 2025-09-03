.pulse {
              position: relative;
              width: 20px;
              height: 20px;
              background: rgba(0, 123, 255, 0.5);  /* default blue */
              border-radius: 50%;
            }
            .pulse::after {
              content: "";
              position: absolute;
              width: 20px;
              height: 20px;
              border-radius: 50%;
              background: inherit;
              animation: pulse-animation 2s infinite;
            }
            @keyframes pulse-animation {
              0% { transform: scale(1); opacity: 0.7; }
              70% { transform: scale(3); opacity: 0; }
              100% { transform: scale(1); opacity: 0; }
            }
            .pulse-red { background: rgba(255, 0, 0, 0.5); }
            .pulse-blue { background: rgba(0, 123, 255, 0.5); }
            .pulse-orange { background: rgba(255, 165, 0, 0.5); }