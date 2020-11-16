library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use STD.textio.all;

entity multiply_accumulater_tb is
end multiply_accumulater_tb;

architecture multiply_accumulater_RTL_tb of multiply_accumulater_tb is

	constant clk_period : time := 20 ns;
	
	signal in0_tb, in1_tb, in2_tb, in3_tb, in4_tb, in5_tb, in6_tb, in7_tb : std_logic_vector(31 downto 0);
	signal clk_tb, resetb_tb, MCEN_tb : std_logic;
	signal mult0_tb, mult1_tb, mult2_tb, mult3_tb : std_logic_vector(63 downto 0);
	signal sum0_tb, sum1_tb : std_logic_vector(63 downto 0);
	signal result_tb : std_logic_vector(63 downto 0);
	
	signal clocks_taken_tb : std_logic_vector(7 downto 0);
	
	signal INITIAL_ST_tb, MULT_ST_tb, ADD_ST_tb, MERGE_ST_tb, DONE_ST_tb : std_logic;
	
	signal done_tb : std_logic;
	
	signal clock_count : integer range 0 to 9999;
	signal test_num: integer range 0 to 100;

	component multiply_accumulater
		port(
			input0, input1, inpu2, input3, input4, input5, input6, input7: IN std_logic_vector(31 downto 0);
			clk, resetb, MCEN: IN std_logic;
			sum: OUT std_logic_vector(63 downto 0);
			clock_taken: OUT std_logic_vector(7 downto 0);
			INITIAL_ST, MULT_ST,ADD_ST, MERGE_ST, DONE_ST: OUT std_logic;
			done: OUT std_logic
		);
	end component;

begin
	
	UUT : multiply_accumulater
		port map(
			in0_tb, in1_tb, in2_tb, in3_tb, in4_tb, in5_tb, in6_tb, in7_tb,
			clk_tb, resetb_tb, MCEN_tb,
			result_tb,
			clocks_taken_tb,
			INITIAL_ST_tb, MULT_ST_tb, ADD_ST_tb, MERGE_ST_tb, DONE_ST_tb,
			done_tb
		);
	
	MCEN_tb  <= '1';
	resetb_tb <= '0', '1' after (clk_period * 1.1);
	
	clock_generation : process
	begin
		clk_tb <= '0', '1' after(clk_period/2);
		wait for clk_period;
	end process clock_generation;
	
	clock_counting : process (clk_tb, resetb_tb)
	begin
		if (resetb_tb = '0') then
			clock_count <= 0;
		elsif clk_tb'event and clk_tb = '1' then
			clock_count <= clock_count + 1;
		end if;
	end process clock_counting;
	
	
		Stim_multiply_accumulater: process
			file out_file : TEXT open WRITE_MODE is "output_results.txt" ;
			variable out_line: line;
			
			procedure apply_test (constant in0_value, in1_value, in2_value, in3_value, in4_value, in5_value, in6_value, in7_value : in integer) is
			begin
				in0_tb <= CONV_STD_LOGIC_VECTOR(in0_value, 32);
				in1_tb <= CONV_STD_LOGIC_VECTOR(in1_value, 32);
				in2_tb <= CONV_STD_LOGIC_VECTOR(in2_value, 32);
				in3_tb <= CONV_STD_LOGIC_VECTOR(in3_value, 32);
				in4_tb <= CONV_STD_LOGIC_VECTOR(in4_value, 32);
				in5_tb <= CONV_STD_LOGIC_VECTOR(in5_value, 32);
				in6_tb <= CONV_STD_LOGIC_VECTOR(in6_value, 32);
				in7_tb <= CONV_STD_LOGIC_VECTOR(in7_value, 32);
				
				test_num <= test_num + 1;
				
				wait until clk_tb'event and clk_tb = '1';
				wait for 1 ns;
				wait until (done_tb'event and done_tb = '1');
				wait for 1 ns;
				wait until clk_tb'event and clk_tb = '1';
				wait for 3 ns;
	
				WRITE(out_line, string'("Test #"));
				WRITE(out_line, test_num);
				WRITELINE(out_file, out_line);
	
				WRITE(out_line, string'("input0 = "));
				WRITE(out_line, in0_value);
				WRITE(out_line, string'(", input1 = "));
				WRITE(out_line, in1_value);
				WRITE(out_line, string'(", input2 = "));
				WRITE(out_line, in2_value);
				WRITE(out_line, string'(", input3 = "));
				WRITE(out_line, in3_value);
				WRITE(out_line, string'(", input4 = "));
				WRITE(out_line, in4_value);
				WRITE(out_line, string'(", input5 = "));
				WRITE(out_line, in5_value);
				WRITE(out_line, string'(", input6 = "));
				WRITE(out_line, in6_value);
				WRITE(out_line, string'(", input7 = "));
				WRITE(out_line, in7_value);
				WRITELINE(out_file, out_line);
				
				WRITE(out_line, string'(", mult0 = "));
				WRITE(out_line, CONV_INTEGER(unsigned(mult0_tb)));
				WRITE(out_line, string'(", mult1 = "));
				WRITE(out_line, CONV_INTEGER(unsigned(mult1_tb)));
				WRITE(out_line, string'(", mult2 = "));
				WRITE(out_line, CONV_INTEGER(unsigned(mult2_tb)));
				WRITE(out_line, string'(", mult3 = "));
				WRITE(out_line, CONV_INTEGER(unsigned(mult3_tb)));
				WRITE(out_line, string'(", sum0 = "));
				WRITE(out_line, CONV_INTEGER(unsigned(sum0_tb)));
				WRITE(out_line, string'(", sum1 = "));
				WRITE(out_line, CONV_INTEGER(unsigned(sum1_tb)));
				WRITE(out_line, string'(", merge result = "));
				WRITE(out_line, CONV_INTEGER(unsigned(result_tb)));
				WRITELINE(out_file, out_line);
	
				WRITE(out_line, string'("Number of Clocks taken = "));
				WRITE(out_line, CONV_INTEGER(unsigned(clocks_taken_tb)));
				WRITELINE(out_file, out_line);
				WRITE(out_line , ' '); -- blank line
				WRITELINE(out_file, out_line);
			end procedure apply_test;
		
		begin
			--initial values
			in0_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			in1_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			in2_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			in3_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			in4_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			in5_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			in6_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			in7_tb <= CONV_STD_LOGIC_VECTOR(0, 32);
			
			test_num <= 0;
			
			wait for (clk_period *2);
			
			apply_test (78,48,29,39,23,25,67,83); -- Test #1
			apply_test (407,235,345,666,477,845,543,630); -- Test #2
			apply_test (2551,8325,2144,6478,9082,3477,8234,2359); -- Test #3
			apply_test (87254,14264,92763,17263,19826,72639,36297,17264); -- Test #4
			apply_test (192253,315764,987234,987567,123987,927485,102938,238716); -- Test #5

			WRITE(out_line , string'("All tests concluded."));
			WRITELINE(out_file, out_line);
		
			wait;
	
		end process Stim_multiply_accumulater;
	
end multiply_accumulater_RTL_tb;
