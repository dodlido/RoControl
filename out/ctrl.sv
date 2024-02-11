//| Name: ctrl.sv                            |//
//| Date: 2024-02-12                         |//
//| Description: Automatically generated FSM |//
//| Generated using RoControl python package |//
                                                
module ctrl #() (                               

   input wire [0:0] clk,
   input wire [0:0] rst_n,
   input wire [0:0] vld,
   input wire [0:0] clr,
   output reg [1:0] count
);

typedef enum {
   IDLE,
   S1,
   S2,
   S3,
} State ;
State current_state, next_state ;
always_ff @(posedge clk, negedge rst_n) begin
   if (!rst_n)
      current_state <= IDLE ;
   else
      current_state <= next_state ;
end

always_comb begin
   case(current_state)
      IDLE: begin
         if (vld & !clr)
            next_state = S1;
         else
            next_state = IDLE;
      end
      S1: begin
         if (vld & !clr)
            next_state = S2;
         else if (clr)
            next_state = IDLE;
         else
            next_state = S1;
      end
      S2: begin
         if (vld & !clr)
            next_state = S3;
         else if (clr)
            next_state = IDLE;
         else
            next_state = S2;
      end
      S3: begin
         if (vld & !clr)
            next_state = S1;
         else if (clr)
            next_state = IDLE;
         else
            next_state = S3;
      end
   endcase
end

always_comb begin
   count = 2'b0 ;
   case(current_state)
      IDLE: begin
         if (next_state == S1)
            count = 2'b1;
      end
      S1: begin
         if (next_state == S2)
            count = 2'b10;
         if (next_state == IDLE)
            count = 2'b0;
      end
      S2: begin
         if (next_state == S3)
            count = 2'b11;
         if (next_state == IDLE)
            count = 2'b0;
      end
      S3: begin
         if (next_state == S1)
            count = 2'b1;
         if (next_state == IDLE)
            count = 2'b0;
      end
   endcase
end

endmodule:ctrl

//| Enjoy! Esty                                  |//
